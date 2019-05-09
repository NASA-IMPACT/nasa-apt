#!/bin/sh

aws s3 cp s3://nasa-apt-scripts/serialize.py /app
aws s3 cp s3://nasa-apt-scripts/ATBD.tex /app
aws s3 cp s3://nasa-apt-scripts/supplemental_requirements.txt /app

pip install -r supplemental_requirements.txt

aws s3 cp s3://$1/$2 .

if [ $? -eq 0 ]; then
    echo 'Successfully retrieved JSON file from s3://'$1'/'$2
else
    echo 'Failed to retrieve original JSON file'
fi

texName=$(python3 serialize.py $2)

if [ $? -eq 0 ]; then
    echo 'Successfully wrote TeX file'$texName
else
    echo 'Failed to write TeX file'
fi

aws s3 cp $texName s3://$3/$texName --acl public-read
aws s3 cp main.bib s3://$3/$(echo $texName|cut -d. -f1).bib --acl public-read

if [ $? -eq 0 ]; then
    echo 'Successfully saved to s3://'$3'/'$texName
else
    echo 'Failed to write to s3'
fi