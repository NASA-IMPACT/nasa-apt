"""
CDK Stack definition code for NASA APT API
"""
import os
from typing import Any

import aws_cdk.aws_apigatewayv2_alpha as apigw
import aws_cdk.aws_apigatewayv2_integrations_alpha as apigw_integrations
import config
from aws_cdk import App, Aspects, CfnOutput, Duration, RemovalPolicy, Stack, Tags
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_event_sources as lambda_event_source
from aws_cdk import aws_opensearchservice as opensearch
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_sqs as sqs
from constructs import Construct
from permissions_boundary import PermissionBoundaryAspect


class nasaAPTLambdaStack(Stack):
    """
    NASA APT Lambda Stack
    This code is freely adapted from:
    - https://github.com/leothomas/titiler/blob/10df64fbbdd342a0762444eceebaac18d8867365/stack/app.py author: @leothomas
    - https://github.com/ciaranevans/titiler/blob/3a4e04cec2bd9b90e6f80decc49dc3229b6ef569/stack/app.py author: @ciaranevans
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        memory: int = 1024,
        timeout: int = 60 * 2,
        concurrent: int = 100,
        code_dir: str = "./",
        **kwargs: Any,
    ) -> None:
        """Define stack."""
        super().__init__(scope, id, **kwargs)

        if config.GCC_MODE:
            print("DEPLOYING WITH GCC PERMISSIONS BOUNDARY APPLIED")
            permission_boundary = iam.ManagedPolicy.from_managed_policy_name(
                self, "PermissionsBoundary", "mcp-tenantOperator-APIG"
            )
            Aspects.of(self).add(PermissionBoundaryAspect(permission_boundary))

        if config.GCC_MODE and not config.VPC_ID:
            raise Exception(
                "Unable to create VPC in GCC, please use pre-configured VPC. Contact GCC admin for more info"
            )

        if config.VPC_ID:
            vpc = ec2.Vpc.from_lookup(self, f"{id}-vpc", vpc_id=config.VPC_ID)
        else:
            vpc = ec2.Vpc(
                self,
                id=f"{id}-vpc",
                cidr="10.0.0.0/16",
                max_azs=2,
                nat_gateways=1,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name="public-subnet",
                        subnet_type=ec2.SubnetType.PUBLIC,
                        cidr_mask=24,
                    ),
                    ec2.SubnetConfiguration(
                        name="private-subnet",
                        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                        cidr_mask=28,
                    ),
                ],
            )

        rds_security_group = ec2.SecurityGroup(
            self,
            id=f"{id}-rds-security-group",
            vpc=vpc,
            description=f"Security group for {id}-rds",
        )

        lambda_security_group = ec2.SecurityGroup(
            self,
            id=f"{id}-lambda-security-group",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {id}-lambda",
        )

        os_vpc_security_group = ec2.SecurityGroup(
            self,
            id=f"{id}-opensearch-security-group",
            vpc=vpc,
            description=f"Security group for {id}-opensearch in a VPC",
        )

        os_vpc_security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.tcp(80),
            description="Allow traffic from the Lambda Security Group on port 80",
        )

        rds_security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.tcp(5432),
            description="Allow traffic to Postgres Security Group from Lambda Security Group",
        )

        # Grant ingress from the VPC's CIDR, which allows access from an EC2 jumpbox
        # hosted in the VPC
        if config.GCC_MODE:
            rds_security_group.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
                connection=ec2.Port.tcp(5432),
                description="Allow ssh traffic from bastion host EC2 for sqitch deployment",
            )

        # TODO: add bootstrapping lambda as a custom resource to be run by cloudformation

        rds_params = dict(
            credentials=rds.Credentials.from_generated_secret(
                username="masteruser", secret_name=f"{id}-db-secrets"
            ),
            allocated_storage=10,
            vpc=vpc,
            security_groups=[rds_security_group],
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            # Upgraded to t3 small RDS instance since t2 small no longer
            # supports postgres 13+
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL
            ),
            instance_identifier=f"{id}-db-encrypt",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            publicly_accessible=True,
            database_name="nasadb",
            backup_retention=Duration.days(7),
            deletion_protection="prod" in config.STAGE.lower(),
            removal_policy=RemovalPolicy.SNAPSHOT,
            storage_encrypted=True,
        )
        if config.GCC_MODE:
            rds_params["vpc_subnets"] = ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            )
            rds_params["publicly_accessible"] = False

        if config.DATABASE_FROM_SNAPSHOT_ID:
            rds_params["snapshot_identifier"] = config.DATABASE_FROM_SNAPSHOT_ID
            rds_params.pop("storage_encrypted")
            rds_params.pop("database_name")
            rds_params["credentials"] = rds.SnapshotCredentials.from_generated_secret(
                username="masteruser"
            )
            database = rds.DatabaseInstanceFromSnapshot(
                self, f"{id}-postgres-database-encrypt", **rds_params
            )
        else:
            database = rds.DatabaseInstance(
                self, f"{id}-postgres-database-encrypt", **rds_params
            )
        CfnOutput(
            self,
            f"{id}-database-secret-arn",
            value=database.secret.secret_arn,
            description=(
                "Arn of the SecretsManager instance holding the connection info for Postgres DB"
            ),
        )

        bucket_params = dict(
            scope=self,
            id=f"{id}",
            removal_policy=RemovalPolicy.RETAIN
            if "prod" in config.STAGE.lower()
            else RemovalPolicy.DESTROY,
        )
        if config.S3_BUCKET:
            bucket_params["bucket_name"] = config.S3_BUCKET
        bucket = s3.Bucket(**bucket_params)

        visibility_timeout = timeout * 2
        sqs_queue = sqs.Queue(
            self,
            f"{id}-queue",
            # how long to wait before a retry
            visibility_timeout=Duration.seconds(visibility_timeout),
            # how long to keep messages in the queue
            retention_period=Duration.seconds(visibility_timeout * config.MAX_RETRIES),
        )

        # This domain is launched within a VPC
        private_os_domain = opensearch.Domain(
            self,
            f"{id}-osdomain",
            version=opensearch.EngineVersion.OPENSEARCH_1_0,
            capacity=opensearch.CapacityConfig(
                data_node_instance_type="t3.small.search",
                data_nodes=1,
            ),
            vpc=vpc,
            vpc_subnets=[
                ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    one_per_az=True,
                    availability_zones=sorted(vpc.availability_zones)[:1],
                )
            ],
            security_groups=[os_vpc_security_group],
            # slice last 28 chars since OPEN Domains can't have a name longer than 28 chars in
            # AWS (and can't start with a `-` character)
            domain_name=f"{id}-osdomain"[-28:].strip("-"),
            ebs=opensearch.EbsOptions(
                enabled=True,
                iops=0,
                volume_size=10,
                volume_type=ec2.EbsDeviceVolumeType.GP2,
            ),
            automated_snapshot_start_hour=0,
            removal_policy=RemovalPolicy.RETAIN
            if "prod" in config.STAGE.lower()
            else RemovalPolicy.DESTROY,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
        )

        ses_access = iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"])
        sqs_access = iam.PolicyStatement(actions=["sqs:SendMessage"], resources=["*"])

        frontend_url = config.FRONTEND_URL
        lambda_env = dict(
            PROJECT_NAME=config.PROJECT_NAME,
            API_VERSION_STRING=config.API_VERSION_STRING,
            APT_FRONTEND_URL=frontend_url,
            BACKEND_CORS_ORIGINS=config.BACKEND_CORS_ORIGINS,
            POSTGRES_ADMIN_CREDENTIALS_ARN=database.secret.secret_arn,
            OPENSEARCH_URL=private_os_domain.domain_endpoint,
            TASK_QUEUE_URL=sqs_queue.queue_url,
            S3_BUCKET=bucket.bucket_name,
            NOTIFICATIONS_FROM=config.NOTIFICATIONS_FROM,
            APT_FEATURE_MFA_ENABLED=config.APT_FEATURE_MFA_ENABLED,
            APT_FEATURE_JOURNAL_PDF_EXPORT_ENABLED=config.APT_FEATURE_JOURNAL_PDF_EXPORT_ENABLED,
            APT_FEATURE_PDF_EXPORT_DEBUG=config.APT_FEATURE_PDF_EXPORT_DEBUG,
            MODULE_NAME="nasa_apt.main",
            VARIABLE_NAME="app",
        )

        api_handler_lambda_props = dict(
            runtime=_lambda.Runtime.FROM_IMAGE,
            code=_lambda.Code.from_asset_image(
                directory=code_dir,
                file="app/Dockerfile",
                entrypoint=["/usr/bin/python3", "-m", "awslambdaric"],
                cmd=["handler.handler"],
            ),
            handler=_lambda.Handler.FROM_IMAGE,
            memory_size=memory,
            timeout=Duration.seconds(timeout),
            environment=lambda_env,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_security_group],
        )

        if concurrent:
            api_handler_lambda_props["reserved_concurrent_executions"] = concurrent

        api_handler_lambda = _lambda.Function(
            self, f"{id}-lambda", **api_handler_lambda_props
        )
        api_handler_lambda.add_to_role_policy(ses_access)
        api_handler_lambda.add_to_role_policy(sqs_access)
        database.secret.grant_read(api_handler_lambda)
        """account or service principal rights to read/write the opensearch domain note that this will vary depending on deployment destination"""
        os_access_policy = iam.PolicyStatement(sid="osAccessPolicy")
        os_access_policy.add_arn_principal(f"{api_handler_lambda.function_arn}")
        os_access_policy.add_actions("es:ESHttp*")

        # assign opensearch access policy to the private open search domain
        os_access_policy.add_resources(f"{private_os_domain.domain_arn}/*")

        # grant lambda read/write for private opensearch domain
        private_os_domain.grant_read_write(api_handler_lambda)

        bucket.grant_read_write(api_handler_lambda)

        # defines an API Gateway Http API resource backed by our custom lambda function.
        api_gateway = apigw.HttpApi(
            self,
            f"{id}-endpoint",
            default_integration=apigw_integrations.HttpLambdaIntegration(
                f"{id}-apigw-lambda-integration", handler=api_handler_lambda
            ),
        )
        CfnOutput(
            self,
            f"{id}-endpoint-url",
            value=api_gateway.api_endpoint,
            description="API Gateway endpoint for the APT API",
        )

        sqs_handler_lambda_props = dict(
            runtime=_lambda.Runtime.FROM_IMAGE,
            code=_lambda.Code.from_asset_image(
                directory=code_dir,
                file="app/Dockerfile",
                entrypoint=["/usr/bin/python3", "-m", "awslambdaric"],
                cmd=["handler.tasks_handler"],
            ),
            handler=_lambda.Handler.FROM_IMAGE,
            memory_size=memory,
            timeout=Duration.seconds(timeout),
            environment=lambda_env,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_security_group],
        )

        if concurrent:
            sqs_handler_lambda_props["reserved_concurrent_executions"] = concurrent

        sqs_handler_lambda = _lambda.Function(
            self, f"{id}-sqs-handler-lambda", **sqs_handler_lambda_props
        )
        bucket.grant_read_write(sqs_handler_lambda)
        database.secret.grant_read(sqs_handler_lambda)

        os_access_policy.add_arn_principal(f"{sqs_handler_lambda.function_arn}")
        private_os_domain.grant_read_write(sqs_handler_lambda)

        # attach the task handling lambda to the queue
        sqs_event_source = lambda_event_source.SqsEventSource(sqs_queue)
        sqs_handler_lambda.add_event_source(sqs_event_source)

        user_pool = cognito.UserPool(
            self,
            f"{id}-users",
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True, username=False),
            standard_attributes=cognito.StandardAttributes(
                preferred_username=cognito.StandardAttribute(
                    mutable=True, required=True
                )
            ),
            user_pool_name=f"{id}-users",
            user_verification=cognito.UserVerificationConfig(
                # TODO: this email body can contain HTML tags for a better user experience
                email_subject="Your Algorithm Publication Tool (APT) account",
                email_body=(
                    "Dear APT user,<br>"
                    "<br>"
                    "Your Algorithm Publication Tool (APT) account has been created. Please verify your account by clicking on {##Verify Email##}. Your account only needs to be verified once.<br>"
                    "<br>"
                    f"Please review the user agreement statement below, then access your APT account by clicking <a href='{frontend_url.strip('/')}/signin'>here</a>.<br>"
                    "<br>"
                    "NASA ALGORITHM PUBLICATION TOOL (APT) POLICY / USER AGREEMENT STATEMENT NASA IT Consent Banner | NASA-SPEC-2669 Version 1.0<br>"
                    "<br>"
                    "By accessing and using this information system, you acknowledge and consent to the following: You are accessing a U.S. Government information system, which includes:<br>"
                    "<br>"
                    "(1) this computer; (2) this computer network; (3) all computers connected to this network including end user systems (4) all devices and storage media attached to this network or to any computer on this network; and (5) cloud and remote information services. This information system is provided for U.S. Government-authorized use only. You have no reasonable expectation of privacy regarding any communication transmitted through or data stored on this information system. At any time, and for any lawful purpose, the U.S. Government may monitor, intercept, search, and seize any communication or data transiting, stored on, or traveling to or from this information system. You are NOT authorized to process classified information on this information system. Unauthorized or improper use of this system may result in suspension or loss of access privileges, disciplinary action, and civil and/or criminal penalties.<br>"
                    "<br>"
                    "By accepting APT account access, you acknowledge that you have read, understand, and agree to abide by the NASA APT POLICY / USER AGREEMENT STATEMENT as written above.<br>"
                    "<br>"
                    "By accepting APT account access, you acknowledge that you have read, understand, and agree to abide by the APT Access Control Policy Statement as written in this document: <a href='https://docs.google.com/document/d/1zSNTAmC1LIFZh__Y5vIgP6VaxnZ4r9OO-jWBt0Lv08I/edit?usp=sharing'>https://docs.google.com/document/d/1zSNTAmC1LIFZh__Y5vIgP6VaxnZ4r9OO-jWBt0Lv08I/edit?usp=sharing</a><br>"
                    "<br>"
                    "Sincerely,<br>"
                    "The NASA APT Team"
                ),
                email_style=cognito.VerificationEmailStyle.LINK,
            ),
            sign_in_case_sensitive=False,
            removal_policy=RemovalPolicy.RETAIN
            if "prod" in config.STAGE.lower()
            else RemovalPolicy.DESTROY,
        )

        for lambda_function in [api_handler_lambda, sqs_handler_lambda]:
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["cognito-idp:AdminGetUser"],
                    resources=[user_pool.user_pool_arn],
                )
            )
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "cognito-idp:ListUserPools",
                        "cognito-idp:ListUserPoolClients",
                        "cognito-idp:ListUsersInGroup",
                    ],
                    resources=["*"],
                )
            )

        CfnOutput(
            self,
            f"{id}-userpool-id",
            value=user_pool.user_pool_id,
            description="User Pool ID",
        )

        app_client = user_pool.add_client(
            f"{id}-apt-app-client",
            auth_flows=cognito.AuthFlow(user_password=True),
            o_auth=cognito.OAuthSettings(
                callback_urls=[config.FRONTEND_URL, "http://localhost:9000"],
                logout_urls=[config.FRONTEND_URL, "http://localhost:9000"],
                flows=cognito.OAuthFlows(implicit_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE,
                    # TODO: verify if all these scopes are required
                    cognito.OAuthScope.COGNITO_ADMIN,
                ],
            ),
            # As a security measure, this sends an error message
            # that is NOT UserNotFoundError, to avoid revealing user
            # absence.
            prevent_user_existence_errors=False,
            user_pool_client_name=f"{id}-apt-app-client",
        )

        CfnOutput(
            self,
            f"{id}-app-client-id",
            value=app_client.user_pool_client_id,
            description="User Pool App Client ID",
        )

        domain = user_pool.add_domain(
            f"{id}-apt-app-client-domain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix=f"{id}"),
        )

        CfnOutput(
            self,
            f"{id}-domain",
            value=domain.domain_name,
            description="User pool domain",
        )

        for lambda_function in [api_handler_lambda, sqs_handler_lambda]:
            lambda_function.add_environment(
                key="USER_POOL_NAME",
                value=user_pool.node.id,
            )
            lambda_function.add_environment(
                key="APP_CLIENT_NAME", value=app_client.user_pool_client_name
            )


app = App()


# Tag infrastructure
for key, value in {
    "Project": config.PROJECT_NAME,
    "Stack": config.STAGE,
    "Owner": config.OWNER,
    "Client": config.CLIENT,
}.items():
    if value:
        Tags.of(app).add(key, value)


lambda_stackname = f"{config.PROJECT_NAME}-{config.STAGE}"
lambda_stackdescription = f"Deploys resources for backend APT {config.PROJECT_NAME}-{config.STAGE} to DevSeed AWS cloud account"
nasaAPTLambdaStack(
    app,
    lambda_stackname,
    memory=config.MEMORY,
    timeout=config.TIMEOUT,
    concurrent=config.MAX_CONCURRENT,
    env=dict(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

app.synth()
