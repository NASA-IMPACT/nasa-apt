#!/bin/sh

aws s3 cp s3://$1/$2 .
pdflatex --shell-escape $2
aws s3 cp test_json.pdf s3://$1/$(echo $2|cut -d. -f1).pdf