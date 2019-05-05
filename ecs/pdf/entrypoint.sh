#!/bin/sh

aws s3 cp s3://$1/$2 .
pdflatex --shell-escape "\def\convertType{PDF}\input{$2}"
aws s3 cp $(echo $2|cut -d. -f1).pdf s3://$1/$(echo $2|cut -d. -f1).pdf --acl public-read