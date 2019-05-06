#### First, load your AWS credentials into environment variables:
```
export AWS_ACCESS_KEY=
export AWS_SECRET_ACCESS_KEY=
```

#### Build and run the image which creates the TeX file:
Inputs:
* Name of the bucket in which the JSON file is stored
* Name of the JSON file
* Name of the bucket the TeX file should be written to
```
docker build tex -t tex

docker run -e AWS_ACCESS_KEY=$AWS_ACCESS_KEY -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY tex <input bucket name> <JSON file name> <output bucket name> 
```
Output: `s3://<output bucket name>/<filename>.tex`

#### Build and run the image which creates the PDF from the TeX file:
Inputs:
* Name of the bucket in which the TeX file is stored
* Name of the TeX file
```
docker build pdf -t pdf
docker run -e AWS_ACCESS_KEY=$AWS_ACCESS_KEY -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY pdf <bucket name> <TeX file name>
```
Output: `s3://<bucket name>/<filename>.pdf`

#### Build and run the image which creates the HTML folder from the TeX file:
Inputs:
* Name of the bucket in which the TeX file is stored
* Name of the TeX file
```
docker build html -t html
docker run -e AWS_ACCESS_KEY=$AWS_ACCESS_KEY -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY html <bucket name> <TeX file name>
```
Outputs: 
```
s3://<bucket name>/<filename>/index.html
s3://<bucket name>/<filename>/dist/javascript/index.js
s3://<bucket name>/<filename>/dist/css/index.css
```



