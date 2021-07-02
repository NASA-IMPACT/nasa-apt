wait_for_service() {
  echo "Waiting for $1 at address http://localstack:4566/health, attempting every 2s"
  until $(curl --silent --fail http://localstack:4566/health | grep "\"$1\": \"running\"" > /dev/null); do
      printf '.'
      sleep 2
  done
  echo "Success: Reached $1"
}
wait_for_service "secretsmanager"
aws --endpoint-url http://localstack:4566 secretsmanager create-secret --name "${POSTGRES_ADMIN_CREDENTIALS_ARN}" --secret-string '{"username": "'"${POSTGRES_USER}"'","password": "'"${POSTGRES_PASSWORD}"'","port": 5432,"dbname": "'"${POSTGRES_DB}"'","host": "db"}' 

# No need to mess around with ACL - according to @ciaranevans localstack free has no concept of 
# IAM roles and access control.
wait_for_service "s3"
aws --endpoint-url http://localstack:4566 s3 mb s3://"${S3_BUCKET}" 

aws --endpoint-url http://localstack:4566 s3 cp "fixture_data/figures/fullmoon.jpg" "s3://${S3_BUCKET}/1/images/fullmoon.jpg"
aws --endpoint-url http://localstack:4566 s3 cp "fixture_data/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-0.pdf"
aws --endpoint-url http://localstack:4566 s3 cp "fixture_data/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-1.pdf"
aws --endpoint-url http://localstack:4566 s3 cp "fixture_data/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-0-journal.pdf"
aws --endpoint-url http://localstack:4566 s3 cp "fixture_data/figures/test-atbd-1-v1-0.pdf" "s3://${S3_BUCKET}/1/pdf/test-atbd-1-v1-1-journal.pdf"

wait_for_service "cognito-idp"
wait_for_service "cognito-identity"

#pool_id = $(aws --endpoint-url http://localstack:4566 cognito-idp list-user-pools --no-sign-request --max-results 60 | jq -rc "select(.UserPools|length==1)")

# Cognito setup
pool_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool --pool-name ${USER_POOL_NAME} | jq -rc ".UserPool.Id")
client_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool-client --user-pool-id ${pool_id} --client-name ${APP_CLIENT_NAME} | jq -rc ".UserPoolClient.ClientId")

echo "USER POOL ID: ${pool_id}"
echo "APP CLIENT ID: ${client_id}"

user_sub=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username test@example.com --user-attributes '[{"Name":"preferred_username","Value":"Test User"}, {"Name":"email","Value":"test@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')

echo "USER SUB: ${user_sub}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username test@example.com --password Password123! --permanent

sqitch deploy --verify db:pg://masteruser:password@db:5432/nasadb &&
psql 'postgres://masteruser:password@db:5432/nasadb?options=--search_path%3dapt' -v user_sub="${user_sub}" -f fixture_data/testData.sql