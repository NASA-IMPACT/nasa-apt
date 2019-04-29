psql $(aws cloudformation list-exports --region us-east-1 --query "Exports[?Name==\`nasa-apt-PGConnection\`].Value" --output text) -f ../init.sql
