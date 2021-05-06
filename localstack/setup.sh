awslocal secretsmanager create-secret --name "${POSTGRES_ADMIN_CREDENTIALS_ARN}" --secret-string '{"username": "'"${POSTGRES_USER}"'","password": "'"${POSTGRES_PASSWORD}"'","port": 5432,"dbname": "'"${POSTGRES_DB}"'","host": "db"}' 

# No need to mess around with ACL - according to @ciaranevans localstack free has no concept of 
# IAM roles and access control.
awslocal s3 mb s3://"${S3_BUCKET}" 

# I know this file will get uploaded 2x - once in the loop above and once here
# TODO: upload it only once
awslocal s3 cp "/figures/fullmoon.jpg" "s3://${S3_BUCKET}/1/images/fullmoon.jpg"
awslocal s3 cp "/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-0.pdf"
awslocal s3 cp "/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-1.pdf"
