#!/bin/sh

aws s3 cp s3://$1/$2 .

if [ $? -eq 0 ]; then
    echo 'Successfully retrieved TeX file from s3://'$1'/'$2 
else
    echo 'Failed to retrieve TeX file'
fi

aws s3 cp s3://$1/$(echo $2|cut -d. -f1).bib main.bib

pdflatex --shell-escape "\def\convertType{PDF}\input{$2}"
bibtex $(echo $2|cut -d. -f1)
pdflatex --shell-escape "\def\convertType{PDF}\input{$2}"
bibtex $(echo $2|cut -d. -f1)
pdflatex --shell-escape "\def\convertType{PDF}\input{$2}"

if [ $? -eq 0 ]; then
    echo 'Successfully wrote TeX file'$texName
else
    echo 'Failed to write TeX file'
fi

aws s3 cp $(echo $2|cut -d. -f1).pdf s3://$1/$(echo $2|cut -d. -f1).pdf --acl public-read

if [ $? -eq 0 ]; then
    echo 'Successfully saved to s3://'$1'/'$(echo $2|cut -d. -f1)'.pdf'
else
    echo 'Failed to write to s3'
fi