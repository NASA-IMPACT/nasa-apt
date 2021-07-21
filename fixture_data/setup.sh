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


# Cognito setup
pool_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool --pool-name ${USER_POOL_NAME} | jq -rc ".UserPool.Id")
client_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool-client --user-pool-id ${pool_id} --client-name ${APP_CLIENT_NAME} | jq -rc ".UserPoolClient.ClientId")

echo "USER POOL ID: ${pool_id}"
echo "APP CLIENT ID: ${client_id}"
 
# Create test users (curators, authors, reviewers and an owner)
curator_sub=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username curator@example.com --user-attributes '[{"Name":"preferred_username","Value":"CuratorUser"}, {"Name":"email","Value":"curator@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username curator@example.com --password Password123! --permanent
echo "Curator sub: ${curator_sub}"

owner_sub=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username owner@example.com --user-attributes '[{"Name":"preferred_username","Value":"OwnerUser"}, {"Name":"email","Value":"owner@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username owner@example.com --password Password123! --permanent
echo "Owner sub: ${owner_sub}"

author_sub_1=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author1@example.com --user-attributes '[{"Name":"preferred_username","Value":"AuthorUser1"}, {"Name":"email","Value":"author1@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author1@example.com --password Password123! --permanent
echo "Author sub 1: ${author_sub_1}"

author_sub_2=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author2@example.com --user-attributes '[{"Name":"preferred_username","Value":"AuthorUser2"}, {"Name":"email","Value":"author2@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author2@example.com --password Password123! --permanent
echo "Author sub 2: ${author_sub_2}"

author_sub_3=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author3@example.com --user-attributes '[{"Name":"preferred_username","Value":"AuthorUser3"}, {"Name":"email","Value":"author3@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author3@example.com --password Password123! --permanent
echo "Author sub 3: ${author_sub_3}"

reviewer_sub_1=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer1@example.com --user-attributes '[{"Name":"preferred_username","Value":"ReviewerUser1"}, {"Name":"email","Value":"reviwer1@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer1@example.com --password Password123! --permanent
echo "Reviwers sub 1: ${reviewer_sub_1}"

reviewer_sub_2=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer2@example.com --user-attributes '[{"Name":"preferred_username","Value":"ReviewerUser2"}, {"Name":"email","Value":"reviewer2@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer2@example.com --password Password123! --permanent
echo "Reviewer sub 2: ${reviewer_sub_2}"

reviewer_sub_3=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer3@example.com --user-attributes '[{"Name":"preferred_username","Value":"ReviewerUser3"}, {"Name":"email","Value":"reviewer3@example.com"}]' | jq -rc '.User.Attributes[] | select(.Name=="sub")| .Value')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer3@example.com --password Password123! --permanent
echo "Reviewer sub 3: ${reviewer_sub_3}"

# Create curator group and add curator user to it
aws --endpoint-url http://localstack:4566 cognito-idp create-group --group-name curator --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name curator --username curator@example.com --user-pool-id "${pool_id}"

# Create contributor group and add authors and reviewers to it
aws --endpoint-url http://localstack:4566 cognito-idp create-group --group-name contributor --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username owner@example.com --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username author1@example.com --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username author2@example.com --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username author3@example.com --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username reviewer1@example.com --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username reviewer2@example.com --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username reviewer3@example.com --user-pool-id "${pool_id}"

sqitch deploy --verify db:pg://masteruser:password@db:5432/nasadb &&
psql 'postgres://masteruser:password@db:5432/nasadb?options=--search_path%3dapt'  -f fixture_data/testData.sql \
  -v owner_sub="${owner_sub}" \
  -v author_sub_1="${author_sub_1}" \
  -v author_sub_2="${author_sub_2}" \
  -v reviewer_sub_1="${reviewer_sub_1}" \
  -v reviewer_sub_2="${reviewer_sub_2}" 


  