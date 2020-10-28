#!/bin/bash
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
psql -e -1 -v ON_ERROR_STOP=1 $todb <<EOSQL
SET SEARCH_PATH to apt, public;

CREATE OR REPLACE FUNCTION change_notification() RETURNS TRIGGER AS \$\$
DECLARE
atbd_id int;
BEGIN
IF TG_TABLE_NAME = 'contacts' THEN
    SELECT INTO atbd_id c.atbd_id from atbd_contacts c WHERE contact_id=NEW.contact_id;
ELSIF TG_TABLE_NAME = 'contact_groups' THEN
    SELECT INTO atbd_id c.atbd_id from atbd_contact_groups c WHERE contact_group_id=NEW.contact_group_id;
ELSE
    atbd_id = NEW.atbd_id;
END IF;
PERFORM pg_notify('atbd',atbd_id::text);
RETURN NEW;
END;
\$\$ LANGUAGE PLPGSQL;
EOSQL

pg_dump -a --schema=apt  $fromdb | \
  sed -e "s|${fromurl}|${tourl}|g" \
  -e "s|'search_path', ''|'search_path', 'apt, public'|g" | \
  psql -e -1 -v ON_ERROR_STOP=1 $todb
