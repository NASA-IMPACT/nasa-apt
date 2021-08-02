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
pool_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool --pool-name ${USER_POOL_NAME} --username-attributes "email" --policies '{
      "PasswordPolicy": {
        "MinimumLength": 8,
        "RequireUppercase": true,
        "RequireLowercase": true,
        "RequireNumbers": true,
        "RequireSymbols": true,
        "TemporaryPasswordValidityDays": 7
      }
    }' --schema '[
      {
        "Name": "sub",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": false,
        "Required": true,
        "StringAttributeConstraints": {
          "MinLength": "1",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "name",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "given_name",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "family_name",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "middle_name",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "nickname",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "preferred_username",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": true,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "profile",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "picture",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "website",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "email",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "email_verified",
        "AttributeDataType": "Boolean",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false
      },
      {
        "Name": "gender",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "birthdate",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "10",
          "MaxLength": "10"
        }
      },
      {
        "Name": "zoneinfo",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "locale",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "phone_number",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "phone_number_verified",
        "AttributeDataType": "Boolean",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false
      },
      {
        "Name": "address",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "StringAttributeConstraints": {
          "MinLength": "0",
          "MaxLength": "2048"
        }
      },
      {
        "Name": "updated_at",
        "AttributeDataType": "Number",
        "DeveloperOnlyAttribute": false,
        "Mutable": true,
        "Required": false,
        "NumberAttributeConstraints": {
          "MinValue": "0"
        }
      }
    ]' --auto-verified-attributes "email" | jq -rc ".UserPool.Id")
client_id=$(aws --endpoint-url http://localstack:4566 cognito-idp create-user-pool-client --user-pool-id ${pool_id} --client-name ${APP_CLIENT_NAME} | jq -rc ".UserPoolClient.ClientId")

echo "USER POOL ID: ${pool_id}"
echo "APP CLIENT ID: ${client_id}"
 
# Create test users (curators, authors, reviewers and an owner)
curator_sub=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username curator@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Carlos Curator"}, {"Name":"email","Value":"curator@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username curator@example.com --password Password123! --permanent 
echo "Curator sub: ${curator_sub}"

owner_sub=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username owner@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Owner Olivia"}, {"Name":"email","Value":"owner@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username owner@example.com --password Password123! --permanent 
#aws --endpoint-url http://localstack:4566 cognito-idp admin-confirm-sign-up --user-pool-id "${pool_id}"  --username owner@example.com
echo "Owner sub: ${owner_sub}"

author_sub_1=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author1@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Andre Author"}, {"Name":"email","Value":"author1@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author1@example.com --password Password123! --permanent
echo "Author sub 1: ${author_sub_1}"

author_sub_2=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author2@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Anita Author"}, {"Name":"email","Value":"author2@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author2@example.com --password Password123! --permanent
echo "Author sub 2: ${author_sub_2}"

author_sub_3=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username author3@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Allison Author"}, {"Name":"email","Value":"author3@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username author3@example.com --password Password123! --permanent
echo "Author sub 3: ${author_sub_3}"


reviewer_sub_1=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer1@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Ricardo Reviewer"}, {"Name":"email","Value":"reviwer1@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer1@example.com --password Password123! --permanent
echo "Reviwers sub 1: ${reviewer_sub_1}"

reviewer_sub_2=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer2@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Ronald Reviewer"}, {"Name":"email","Value":"reviewer2@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer2@example.com --password Password123! --permanent
echo "Reviewer sub 2: ${reviewer_sub_2}"

reviewer_sub_3=$(aws --endpoint-url http://localstack:4566 cognito-idp admin-create-user --user-pool-id ${pool_id} --username reviewer3@example.com --user-attributes '[{"Name":"email_verified", "Value":"true"},{"Name":"preferred_username","Value":"Rita Reviewer"}, {"Name":"email","Value":"reviewer3@example.com"}]' | jq -rc '.User.Username')
aws --endpoint-url http://localstack:4566 cognito-idp admin-set-user-password --user-pool-id "${pool_id}" --username reviewer3@example.com --password Password123! --permanent



# Create curator group and add curator user to it
aws --endpoint-url http://localstack:4566 cognito-idp create-group --group-name curator --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name curator --username ${curator_sub} --user-pool-id "${pool_id}"

# Create contributor group and add authors and reviewers to it
aws --endpoint-url http://localstack:4566 cognito-idp create-group --group-name contributor --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${owner_sub} --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${author_sub_1} --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${author_sub_2} --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${author_sub_3} --user-pool-id "${pool_id}"

aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${reviewer_sub_1} --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${reviewer_sub_2} --user-pool-id "${pool_id}"
aws --endpoint-url http://localstack:4566 cognito-idp admin-add-user-to-group --group-name contributor --username ${reviewer_sub_3} --user-pool-id "${pool_id}"

wait_for_service "ses"
aws --endpoint-url http://localstack:4566 ses verify-domain-identity --domain example.com --region us-east-1

echo "Applying database migrations"
sqitch deploy --verify db:pg://masteruser:password@db:5432/nasadb &&

echo "Loading test data"
psql 'postgres://masteruser:password@db:5432/nasadb?options=--search_path%3dapt'  -f fixture_data/testData.sql \
  -v owner_sub="${owner_sub}" \
  -v author_sub_1="${author_sub_1}" \
  -v author_sub_2="${author_sub_2}" \
  -v reviewer_sub_1="${reviewer_sub_1}" \
  -v reviewer_sub_2="${reviewer_sub_2}" 


