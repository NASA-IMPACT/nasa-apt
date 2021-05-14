Deployment steps: 
1. install `cdk` 
```bash
npm install -g aws-cdk
```
2. install required packages: 
```bash
pip install -e ".[dev]"
```
3. deploy with cdk
```bash
cdk deploy nasa-apt-lambda-dev # add --profile <profile-name> if using an non-default aws cli account
``` 
