#!/bin/sh
aws s3 cp s3://$1/$2 .
if [ $? -eq 0 ]; then
    echo 'Successfully retrieved TeX file from s3://'$1'/'$2 
else
    echo 'Failed to retrieve TeX file'
fi

aws s3 cp s3://$1/$(echo $2|cut -d. -f1).bib main.bib
engrafo $2 .

if [ $? -eq 0 ]; then
    echo 'Successfully wrote HTML file'
else
    echo 'Failed to write HTML file'
fi

aws s3 cp index.html s3://$1/$(echo $2|cut -d. -f1)/index.html --acl public-read
aws s3 cp dist/javascript/index.js s3://$1/$(echo $2|cut -d. -f1)/dist/javascript/index.js --acl public-read
echo -n '.ltx_graphics {max-width: 100%;height: auto;}' | cat - dist/css/index.css > index.css
aws s3 cp index.css s3://$1/$(echo $2|cut -d. -f1)/dist/css/index.css --acl public-read

if [ $? -eq 0 ]; then
    echo 'Successfully saved files to s3://'$1'/'$(echo $2|cut -d. -f1)
else
    echo 'Failed to write files to s3'
fi