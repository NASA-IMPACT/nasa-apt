from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_apigatewayv2_integrations as apigw_integrations
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as ec2
from aws_cdk import core
from typing import Any
import config
import os


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
        timeout: int = 30,
        concurrent: int = 100,
        code_dir: str = "./",
        **kwargs: Any,
    ) -> None:
        """Define stack."""
        super().__init__(scope, id, **kwargs)

        if config.VPC_ID:
            vpc = ec2.Vpc.from_lookup(self, f"{id}-vpc", vpc_id=config.VPC_ID)
        else:
            vpc = ec2.Vpc(self, id=f"{id}-vpc")

        lambda_function_security_group = ec2.SecurityGroup(
            self, f"{id}-lambda-sg", vpc=vpc
        )
        lambda_function_security_group.add_egress_rule(
            ec2.Peer.any_ipv4(),
            connection=ec2.Port(protocol=ec2.Protocol("ALL"), string_representation=""),
            description="Allow lambda security group all outbound access",
        )

        rds_security_group = ec2.SecurityGroup(
            self,
            f"{id}-rds-sg",
            vpc=vpc,
            # allow_all_outbound=True,
            description=f"Security group for {id}-rds",
        )

        rds_security_group.add_ingress_rule(
            peer=lambda_function_security_group,
            # peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(5432),
            description="Allow Lambda security group access Postgres",
        )

        # TODO: change PASSWORD to use secrets manager
        # TODO: add bootstrapping lambda as a custom resource to be run by cloudformation
        database = rds.DatabaseInstance(
            self,
            f"{id}-postgres-db",
            credentials=rds.Credentials.from_password(
                username="masteruser",
                password=core.SecretValue(
                    value=core.SecretValue.plain_text("password")
                ),
            ),
            allocated_storage=10,
            vpc=vpc,
            # publicly_accessible=True,
            security_groups=[rds_security_group],
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL
            ),
            database_name="nasadb",
            deletion_protection=config.STAGE.lower() == "prod",
            removal_policy=core.RemovalPolicy.SNAPSHOT
            if config.STAGE.lower() == "prod"
            else core.RemovalPolicy.DESTROY,
        )

        # ssm.StringParameter(
        #     self,
        #     id=f"{id}-postgres-password",
        #     # string_value=database.,
        #     parameter_name=f"/integration_tests/{id}/downloader_rds_secret_arn",
        # )

        logs_access = iam.PolicyStatement(
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
            ],
            resources=["*"],
        )
        frontend_url = os.environ["APT_FRONTEND_URL"]
        lambda_env = dict(
            APT_FRONTEND_URL=frontend_url,
            BACKEND_CORS_ORIGINS=os.environ.get(
                "BACKEND_CORS_ORIGINS",
                f"*,http://localhost:3000,http://localhost:3006,{frontend_url}",
            ),
            POSTGRES_HOST=database.instance_endpoint.hostname,
            POSTGRES_USER="masteruser",
            POSTGRES_PASSWORD="password",
            POSTGRES_DB_NAME="nasadb",
            ELASTICURL=os.environ["ELASTICURL"],
            ROOT_PATH=os.environ.get("API_PREFIX", "/"),
            JWT_SECRET=os.environ["JWT_SECRET"],
            FASTAPI_HOST=os.environ["FASTAPI_HOST"],
            IDP_METADATA_URL=os.environ["IDP_METADATA_URL"],
        )
        lambda_env.update(dict(MODULE_NAME="nasa_apt.main", VARIABLE_NAME="app",))

        lambda_function_props = dict(
            runtime=_lambda.Runtime.FROM_IMAGE,
            code=self.create_package(code_dir),
            handler=_lambda.Handler.FROM_IMAGE,
            memory_size=memory,
            timeout=core.Duration.seconds(timeout),
            environment=lambda_env,
            security_groups=[lambda_function_security_group],
            vpc=vpc,
        )

        if concurrent:
            lambda_function_props["reserved_concurrent_executions"] = concurrent

        lambda_function = _lambda.Function(
            self, f"{id}-lambda", **lambda_function_props
        )

        lambda_function.add_to_role_policy(logs_access)

        # defines an API Gateway Http API resource backed by our "dynamoLambda" function.
        apigw.HttpApi(
            self,
            f"{id}-endpoint",
            default_integration=apigw_integrations.LambdaProxyIntegration(
                handler=lambda_function
            ),
        )

    def create_package(self, code_dir: str) -> _lambda.Code:
        """Build docker image and create package."""
        return _lambda.Code.from_asset_image(
            directory=code_dir,
            file="dockerfiles/lambda/Dockerfile",
            repository_name="nasa-apt-api-images",
        )
        # return _lambda.Code.from_asset(
        #     path=os.path.abspath(code_dir),
        #     bundling=core.BundlingOptions(
        #         image=core.BundlingDockerImage.from_asset(
        #             path=os.path.abspath(code_dir),
        #             file="dockerfiles/lambda/Dockerfile",
        #         ),
        #         command=["bash", "-c", "cp -R /var/task/. /asset-output/."],
        #     ),
        # )


app = core.App()


# Tag infrastructure
for key, value in {
    "Project": config.PROJECT_NAME,
    "Stack": config.STAGE,
    "Owner": os.environ.get("OWNER", "Leo Thomas"),
    "Client": os.environ.get("CLIENT", "NASA Impact"),
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
