#!/bin/bash
if [ $# -ne 2]; then
echo <<EOD
# Usage syncdb.sh <name of stack to move data from> <name of stack to move data to>
# This script will update an instance using the data from another instance
# It goes through the following steps
# 1) Gets connection information from cloudformation for each stack
# 2) syncs figures in s3 buckets
# 3) uses pg_dump -a (only dump data) to dump the apt schema from the source data set
# 4) modifies the generated sql to change the url paths in the output
# 5) loads the data into the new database
#    Note: the load is done in a transaction, so if there are any errors,
#          the entire transaction is rolled back
EOD
fi

get_output(){
    echo $outputs | jq --raw-output ".[][] | select(.OutputKey==\"$1\").OutputValue"
}
outputs=`aws cloudformation describe-stacks --region us-east-1 --stack-name $1 --output json --query 'Stacks[*].Outputs[*]'`

fromdb=`get_output PGConnection`
fromfigures=`get_output FiguresBucket`
froms3=`get_output S3Endpoint`
fromurl=${froms3}/${fromfigures}

outputs=`aws cloudformation describe-stacks --region us-east-1 --stack-name $2 --output json --query 'Stacks[*].Outputs[*]'`

todb=`get_output PGConnection`
tofigures=`get_output FiguresBucket`
tos3=`get_output S3Endpoint`
tourl=${tos3}/${tofigures}

echo "syncing data from $fromfigures to $tofigures"
aws s3 sync --delete s3://${fromfigures} s3://${tofigures}

echo "syncing data from $fromdb to $todb while replacing $fromurl with $tourl"

pg_dump -a --schema=apt  $fromdb | \
  sed -e "s|${fromurl}|${tourl}|g" \
  -e "s|'search_path', ''|'search_path', 'apt, public'|g" | \
  psql -e -1 -v ON_ERROR_STOP=1 $todb
