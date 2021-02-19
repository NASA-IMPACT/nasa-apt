from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_apigatewayv2_integrations as apigw_integrations
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda, core
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
            FRONTEND_URL=frontend_url,
            BACKEND_CORS_ORIGINS=os.environ.get(
                "BACKEND_CORS_ORIGINS",
                f"*,http://localhost:3000,http://localhost:3006,{frontend_url}",
            ),
            DBURL=os.environ["DBURL"],
            ELASTICURL=os.environ["ELASTICURL"],
            ROOT_PATH=os.environ.get("API_PREFIX", "/"),
            JWT_SECRET=os.environ["JWT_SECRET"],
            HOST=os.environ["FASTAPI_HOST"],
            IDP_METADATA_URL=os.environ["IDP_METADATA_URL"],
        )
        lambda_env.update(dict(MODULE_NAME="nasa_apt.main", VARIABLE_NAME="app",))

        lambda_function_props = dict(
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=self.create_package(code_dir),
            handler="handler.handler",
            memory_size=memory,
            timeout=core.Duration.seconds(timeout),
            environment=lambda_env,
        )

        if concurrent:
            lambda_function_props["reserved_concurrent_executions"] = concurrent

        lambda_function = aws_lambda.Function(
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

    def create_package(self, code_dir: str) -> aws_lambda.Code:
        """Build docker image and create package."""

        return aws_lambda.Code.from_asset(
            path=os.path.abspath(code_dir),
            bundling=core.BundlingOptions(
                image=core.BundlingDockerImage.from_asset(
                    path=os.path.abspath(code_dir),
                    file="dockerfiles/lambda/Dockerfile",
                ),
                command=["bash", "-c", "cp -R /var/task/. /asset-output/."],
            ),
        )


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
