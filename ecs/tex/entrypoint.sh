#!/bin/sh
aws s3 cp s3://$1/$2 .
texName=$(python3 serialize.py $2)
aws s3 cp $texName s3://$3/$texName --acl public-read

echo 'Successfully saved to s3://'$3'/'$texName