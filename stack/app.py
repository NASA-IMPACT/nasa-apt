"""
CDK Stack definition code for NASA APT API
"""
from typing import Any

import config
from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_apigatewayv2_integrations as apigw_integrations
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticsearch as elasticsearch
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3
from aws_cdk import core


class nasaAPTLambdaStack(core.Stack):
    """
    Covid API Lambda Stack

    This code is freely adapted from
    - https://github.com/leothomas/titiler/blob/10df64fbbdd342a0762444eceebaac18d8867365/stack/app.py author: @leothomas
    - https://github.com/ciaranevans/titiler/blob/3a4e04cec2bd9b90e6f80decc49dc3229b6ef569/stack/app.py author: @ciaranevans

    """

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        memory: int = 1024,
        timeout: int = 60 * 2,
        concurrent: int = 100,
        code_dir: str = "./",
        **kwargs: Any,
    ) -> None:
        """Define stack."""
        super().__init__(scope, id, **kwargs)

        if config.VPC_ID:
            vpc = ec2.Vpc.from_lookup(self, f"{id}-vpc", vpc_id=config.VPC_ID)
        else:
            vpc = ec2.Vpc(
                self,
                id=f"{id}-vpc",
                nat_gateways=0,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name="PublicSubnet1", subnet_type=ec2.SubnetType.PUBLIC
                    )
                ],
            )
        rds_security_group = ec2.SecurityGroup(
            self,
            id=f"{id}-rds-security-group",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {id}-downloader-rds",
        )

        rds_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(5432),
            description="Allow all traffic for Postgres",
        )

        # TODO: add bootstrapping lambda as a custom resource to be run by cloudformation

        database = rds.DatabaseInstance(
            self,
            f"{id}-postgres-db",
            credentials=rds.Credentials.from_generated_secret(
                username="masteruser", secret_name=f"{id}-database-secrets"
            ),
            allocated_storage=10,
            vpc=vpc,
            publicly_accessible=True,
            security_groups=[rds_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL
            ),
            database_name="nasadb",
            backup_retention=core.Duration.days(7),
            deletion_protection=config.STAGE.lower() == "prod",
            removal_policy=core.RemovalPolicy.SNAPSHOT
            if config.STAGE.lower() == "prod"
            else core.RemovalPolicy.DESTROY,
        )

        core.CfnOutput(
            self,
            f"{id}-database-secret-arn",
            value=database.secret.secret_arn,
            description="Arn of the SecretsManager instance holding the connection info for Postgres DB",
        )

        bucket_params = dict(scope=self, id=f"{id}")
        if config.S3_BUCKET:
            bucket_params["bucket_name"] = config.S3_BUCKET
        bucket = s3.Bucket(**bucket_params)

        esdomain = elasticsearch.Domain(
            self,
            f"{id}-elasticsearch-domain",
            version=elasticsearch.ElasticsearchVersion.V7_7,
            capacity=elasticsearch.CapacityConfig(
                data_node_instance_type="t2.small.elasticsearch", data_nodes=1,
            ),
            # slice last 28 chars since Elastic Domains can't have a name longer than 28 chars in AWS
            # (and can't start with a `-` character)
            domain_name=f"{id}-elastic"[-28:].strip("-"),
            ebs=elasticsearch.EbsOptions(
                enabled=True,
                iops=0,
                volume_size=10,
                volume_type=ec2.EbsDeviceVolumeType.GP2,
            ),
            automated_snapshot_start_hour=0,
            access_policies=[
                iam.PolicyStatement(
                    actions=["es:*"],
                    effect=iam.Effect.ALLOW,
                    principals=[
                        iam.ArnPrincipal(f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:root")
                    ],
                    resources=[
                        f"arn:aws:es:${core.Aws.REGION}:${core.Aws.ACCOUNT_ID}:domain/${core.Aws.STACK_NAME}-elastic"
                    ],
                )
            ],
        )
        logs_access = iam.PolicyStatement(
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
            ],
            resources=["*"],
        )
        ses_access = iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"])

        frontend_url = config.FRONTEND_URL
        lambda_env = dict(
            PROJECT_NAME=config.PROJECT_NAME,
            API_VERSION_STRING=config.API_VERSION_STRING,
            APT_FRONTEND_URL=frontend_url,
            BACKEND_CORS_ORIGINS=config.BACKEND_CORS_ORIGINS,
            POSTGRES_ADMIN_CREDENTIALS_ARN=database.secret.secret_arn,
            ELASTICSEARCH_URL=esdomain.domain_endpoint,
            S3_BUCKET=bucket.bucket_name,
        )
        lambda_env.update(dict(MODULE_NAME="nasa_apt.main", VARIABLE_NAME="app",))

        lambda_function_props = dict(
            runtime=_lambda.Runtime.FROM_IMAGE,
            code=_lambda.Code.from_asset_image(
                directory=code_dir,
                file="app/Dockerfile",
                entrypoint=["/usr/local/bin/python", "-m", "awslambdaric"],
                cmd=["handler.handler"],
            ),
            handler=_lambda.Handler.FROM_IMAGE,
            memory_size=memory,
            timeout=core.Duration.seconds(timeout),
            environment=lambda_env,
        )

        if concurrent:
            lambda_function_props["reserved_concurrent_executions"] = concurrent

        lambda_function = _lambda.Function(
            self, f"{id}-lambda", **lambda_function_props
        )
        lambda_function.add_to_role_policy(ses_access)
        lambda_function.add_to_role_policy(logs_access)
        database.secret.grant_read(lambda_function)
        esdomain.grant_read_write(lambda_function)
        bucket.grant_read_write(lambda_function)
        # defines an API Gateway Http API resource backed by our "dynamoLambda" function.

        api_gateway = apigw.HttpApi(
            self,
            f"{id}-endpoint",
            default_integration=apigw_integrations.LambdaProxyIntegration(
                handler=lambda_function
            ),
        )
        core.CfnOutput(
            self,
            f"{id}-endpoint-url",
            value=api_gateway.api_endpoint,
            description="API Gateway endpoint for the APT API",
        )

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
                email_body=(
                    "Thank you for signing up to the Algorithm Publication Tool.<br>Please "
                    "verify you account by clicking on {##Verify Email##}.<br>Sincerely,"
                    "<br>The NASA APT team"
                ),
                email_style=cognito.VerificationEmailStyle.LINK,
            ),
        )

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

        core.CfnOutput(
            self,
            f"{id}-userpool-id",
            value=user_pool.user_pool_id,
            description="User Pool ID",
        )

        app_client = user_pool.add_client(
            f"{id}-apt-app-client",
            auth_flows=cognito.AuthFlow(user_password=True),
            o_auth=cognito.OAuthSettings(
                callback_urls=[config.FRONTEND_URL],
                logout_urls=[config.FRONTEND_URL],
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

        core.CfnOutput(
            self,
            f"{id}-app-client-id",
            value=app_client.user_pool_client_id,
            description="User Pool App Client ID",
        )

        domain = user_pool.add_domain(
            f"{id}-apt-app-client-domain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix=f"{id}"),
        )

        core.CfnOutput(
            self,
            f"{id}-domain",
            value=domain.domain_name,
            description="User pool domain",
        )

        lambda_function.add_environment(
            key="USER_POOL_NAME", value=user_pool.node.id,
        )
        lambda_function.add_environment(
            key="APP_CLIENT_NAME", value=app_client.user_pool_client_name
        )


app = core.App()


# Tag infrastructure
for key, value in {
    "Project": config.PROJECT_NAME,
    "Stack": config.STAGE,
    "Owner": config.OWNER,
    "Client": config.CLIENT,
}.items():
    if value:
        core.Tag.add(app, key, value)


lambda_stackname = f"{config.PROJECT_NAME}-lambda-{config.STAGE}"
nasaAPTLambdaStack(
    app,
    lambda_stackname,
    memory=config.MEMORY,
    timeout=config.TIMEOUT,
    concurrent=config.MAX_CONCURRENT,
)

app.synth()
