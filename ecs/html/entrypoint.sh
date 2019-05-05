#!/bin/sh
aws s3 cp s3://$1/$2 .
engrafo $2 .
aws s3 cp index.html s3://nasa-apt-atbd/$(echo $2|cut -d. -f1)/index.html --acl public-read
aws s3 cp dist/javascript/index.js s3://nasa-apt-atbd/$(echo $2|cut -d. -f1)/dist/javascript/index.js --acl public-read
aws s3 cp dist/css/index.css s3://nasa-apt-atbd/$(echo $2|cut -d. -f1)/dist/css/index.css --acl public-read