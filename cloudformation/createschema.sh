read -p 'Stack name: ' stackname
psql $(aws cloudformation list-exports --region us-east-1 --query \
  "Exports[?Name==\`${stackname}-PGConnection\`].Value" --output text) \
  -f ./createdb.sql
