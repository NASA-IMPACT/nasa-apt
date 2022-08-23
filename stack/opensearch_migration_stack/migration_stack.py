"""
CDK Stack definition code for Open Search Migration
"""
import os
import sys
from typing import Any

import config
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3
from aws_cdk import core

sys.path.append("../")
"""
class contains resources deployed to aid in migrating APT's ElasticSearch instance to an AWS OpenSearch instance
"""
# stack name
migration_stackname = f"{config.PROJECT_NAME}-{config.STAGE}"


class OpensearchMigrationStack(core.Stack):
    """
    This stack is passed on stack/app.py stack.
    Resources included here:
    - KMS key
    -- encrypts the S3 bucket
    - S3 bucket
    -- set to receive snapshots from opensearch domain
    - IAM policies
    -- allows access to the S3 bucket from opensearch, sets a role used for snapshots and opensearch index migrations
    -- allows actions upon ES (Opensearch service) domains
    -- allows opensearch service to assume a role for creating and saving snapshots to an s3 bucket

    """

    def __init__(self, scope: core.Construct, id: str, **kwargs: Any) -> None:
        """Define stack."""
        super().__init__(scope, id, **kwargs)

        # KMS encryption key
        migration_kms_key = kms.Key(self, "apt-opensearch-key")

        # S3 Bucket for migration snapshot(s)
        bucket_params = dict(
            # scope=self,
            id=f"{id}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=migration_kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.RETAIN
            if config.STAGE.lower() == "prod"
            else core.RemovalPolicy.DESTROY,
        )
        if config.S3_BUCKET:
            bucket_params["bucket_name"] = config.MIGRATION_S3_BUCKET

        # create bucket
        migration_bucket = s3.Bucket(self, **bucket_params)
        assert migration_bucket.encryption_key == migration_kms_key

        # IAM Access Policy for s3 migration bucket
        migration_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:DeleteObject", "s3:GetObject", "s3:PutObject"],
                resources=[f"{migration_bucket.bucket_arn}/*"],
                # delegate access permissions to the account principal
                principals=[iam.AccountPrincipal(self.account)],
            )
        )
        # add supporting policy to the same bucket
        migration_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:ListBucket"],
                resources=[f"{migration_bucket.bucket_arn}"],
                principals=[iam.AccountPrincipal(self.account)],
            )
        )

        # Snapshot IAM role which delegates permissions to OpenSearch
        role_description = """"This role allows Opensearch to assume responsibilities for taking an index snapshot from ElasticSearch/OpenSearch and storing it to S3")
        """
        role = iam.Role(
            self,
            id=f"{migration_stackname}-snapshot-role",
            description=role_description,
            assumed_by=iam.ServicePrincipal("opensearchservice.amazonaws.com"),
            role_name=f"{migration_stackname}-snapshot-role",
        )
        # after role is created, attach supporting policies
        if role:

            # var for the elasticsearch domain that is being migrated from
            es_domain_migration_source_arn = (
                "arn:aws:es:us-east-1:552819999234:domain/t-api-lambda-staging-elastic"
            )

            # see sid for comments
            role.attach_inline_policy(
                iam.Policy(
                    self,
                    "{migration_stackname}-snapshot-policy",
                    statements=[
                        iam.PolicyStatement(
                            sid="PassRolePermissionForSnapshotRole",
                            actions=["iam:PassRole"],
                            resources=[f"{role.role_arn}"],
                        ),
                        iam.PolicyStatement(
                            sid="AllowEsHTTPPutOnOpenSearchDomain",
                            actions=["es:ESHttpPut"],
                            resources=[f"{es_domain_migration_source_arn}"],
                        ),
                        iam.PolicyStatement(
                            sid="AllowS3ObjectInteractions",
                            actions=["s3:DeleteObject", "s3:GetObject", "s3:PutObject"],
                            resources=[f"{migration_bucket.bucket_arn}/*"],
                        ),
                        iam.PolicyStatement(
                            sid="AllowS3BucketInteractions",
                            actions=["s3:ListBucket"],
                            resources=[f"{migration_bucket.bucket_arn}"],
                        ),
                    ],
                )
            )


app = core.App()
# create migration stack

OpensearchMigrationStack(
    scope=app,
    id=migration_stackname,
    env=dict(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

app.synth()
