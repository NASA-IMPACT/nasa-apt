"""NASA APT API."""


from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "boto3==1.13.18",
    "botocore==1.16.18",
    # "botostubs==0.12.1.13.18",
    # "certifi==2020.4.5.1",
    # "chardet==3.0.4",
    # "data==0.4",
    # "decorator==4.4.2",
    # "docopt==0.6.2",
    # "docutils==0.15.2",
    "fastapi==0.54.1",
    # "funcsigs==1.0.2",
    # "future==0.18.2",
    "gunicorn==20.0.4",
    # "h11==0.9.0",
    # "httptools==0.1.1",
    # "idna==2.9",
    # "jmespath==0.10.0",
    "latex==0.7.0",
    # "num2words==0.5.10",
    "pandas==1.2.0",
    # "pipreqs==0.4.10",
    "pydantic==1.5.1",
    # "python-dateutil==2.8.1",
    # "pytz==2020.1",
    "requests==2.23.0",
    "requests-aws4auth==1.0",
    # "s3transfer==0.3.3",
    # "shutilwhich==1.1.0",
    # "six==1.15.0",
    # "starlette==0.13.2",
    # "tempdir==0.7.1",
    "uvicorn==0.11.3",
    # "uvloop==0.14.0",
    # "websockets==8.1",
    # "yarg==0.1.9",
    # "itsdangerous==1.1.0",
    # "python3-saml==1.9.0",
    "python-multipart==0.0.5",
    "python-jose==3.2.0",
    "SQLAlchemy==1.3.23",
    "psycopg2-binary==2.8.6",
    # "typing-extensions==3.7.4.3",
    "aiofiles==0.6.0",
    "pylatex==1.4.1",
    "mangum>=0.9.0",
    "awslambdaric==1.2.0"
    # "SQLAlchemy-Utils==0.37.0",
]
extra_reqs = {
    "dev": ["pre-commit", "flake8", "black", "mypy", "isort"],
    "deploy": [
        "python-dotenv",
        "aws-cdk.core>=1.95.0",
        "aws-cdk.aws_lambda>=1.95.0",
        "aws-cdk.aws_apigatewayv2>=1.95.0",
        "aws-cdk.aws_apigatewayv2_integrations>=1.95.0",
        "aws-cdk.aws_iam>=1.95.0",
        "aws-cdk.aws_rds>=1.95.0",
        "aws-cdk.aws_ssm>=1.95.0",
        "aws-cdk.aws_ec2>=1.95.0",
        "aws-cdk.aws_ecs>=1.95.0",
        "aws-cdk.aws_elasticsearch>=1.95.0",
        "aws-cdk.aws_cognito>=1.95.0",
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
    version="2.0.0",
    description=u"API for the NASA Algorith Publication Tool",
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
    author=u"Development Seed",
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
