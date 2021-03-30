awslocal secretsmanager create-secret --name "${POSTGRES_ADMIN_CREDENTIALS_ARN}" --secret-string '{"username": "'"${POSTGRES_USER}"'","password": "'"${POSTGRES_PASSWORD}"'","port": 5432,"dbname": "'"${POSTGRES_DB}"'","host": "db"}' 

# No need to mess around with ACL - according to @ciaranevans localstack free has no concept of 
# IAM roles and access control.
awslocal s3 mb s3://"${S3_BUCKET}" 
# Upload all images
for file in /figures/* 
do 
    awslocal s3 cp ${file} s3://"${S3_BUCKET}"  
done


