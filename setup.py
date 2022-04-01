"""NASA APT API."""


from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "boto3==1.13.18",
    "botocore==1.16.18",
    "fastapi==0.54.1",
    "gunicorn==20.0.4",
    "latex==0.7.0",
    "pandas==1.2.0",
    "pydantic==1.5.1",
    "requests==2.23.0",
    "requests-aws4auth==1.0",
    "python-multipart==0.0.5",
    "python-jose==3.2.0",
    "SQLAlchemy==1.3.23",
    "psycopg2-binary==2.8.6",
    "aiofiles==0.6.0",
    "pylatex==1.4.1",
    "fastapi_permissions==0.2.7",
    "mangum>=0.9.0",
    "awslambdaric==1.2.0",
]
extra_reqs = {
    "dev": ["pre-commit", "flake8", "black==22.3.0", "mypy", "isort"],
    "deploy": [
        "python-dotenv",
        "aws-cdk.core>=1.136.0",
        "aws-cdk.aws_lambda>=1.136.0",
        "aws-cdk.aws_apigatewayv2>=1.136.0",
        "aws-cdk.aws_apigatewayv2_integrations>=1.136.0",
        "aws-cdk.aws_iam>=1.136.0",
        "aws-cdk.aws_rds>=1.136.0",
        "aws-cdk.aws_ssm>=1.136.0",
        "aws-cdk.aws_ec2>=1.136.0",
        "aws-cdk.aws_ecs>=1.136.0",
        "aws-cdk.aws_elasticsearch>=1.136.0",
        "aws-cdk.aws_cognito>=1.136.0",
    ],
    "test": [
        "moto==2.0.8",
        "factory-boy==3.2.0",
        "pytest==6.2.2",
        "pytest-cov==2.12.0",
        "pytest-sqitch==0.1.1",
        "testing-postgresql==1.3.0",
    ],
}


setup(
    name="nasa_apt",
    version="2.2.3-beta",
    description="API for the NASA Algorith Publication Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="",
    author="Development Seed",
    author_email="info@developmentseed.org",
    url="https://github.com/developmentseed/nasa-apt",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    package_data={
        "nasa_apt": ["templates/*.html", "templates/*.xml", "db/static/**/*.json"]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
