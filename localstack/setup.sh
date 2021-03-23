awslocal secretsmanager create-secret --name "${POSTGRES_ADMIN_CREDENTIALS_ARN}" --secret-string '{"username": "'"${POSTGRES_USER}"'","password": "'"${POSTGRES_PASSWORD}"'","port": 5432,"dbname": "'"${POSTGRES_DB}"'","host": "db"}' 

# No need to mess around with ACL - according to @ciaranevans localstack free has no concept of 
# IAM roles and access control.
awslocal s3 mb s3://"${FIGURES_S3_BUCKET}" 
#awslocal s3api put-bucket-acl --bucket "${FIGURES_S3_BUCKET}"  --acl public-read-write
# Upload all images
for file in /figures/* 
do 
    awslocal s3 cp ${file} s3://"${FIGURES_S3_BUCKET}"  
done

# localstack: create s3 bucket for pdfs
awslocal s3 mb s3://"${PDFS_S3_BUCKET}" 
#awslocal s3api put-bucket-acl --bucket "${PDFS_S3_BUCKET}" --acl public-read-write  

