# new-mcp-deploy-bastion

- Status: accepted
- Deciders: MCP Admins <!-- optional -->
- Date: [2023-06-17 when the decision was last updated] 



## Technical Story

Technical Story: A new instance was deployed to MCP for the purposes of manual access and debugging for APT Backend deplyments <!-- optional -->

## Decision Drivers <!-- optional -->

- A standard environment is required for APT deployments when managed manually.
- A secure instance or Operator permissions are required to access resources in the production environment of APT

## Considered Options

- CI/CD automation (in progress)

## Decision Outcome

A new EC2 instance has been deployed to MCP. A jumpbox is required in order to login.
The following has been setup on the deployment EC2.
- Pyenv virtual env
- node
- nvm
- aws cli
- specified packages in `setup.py`

### Positive Consequences <!-- optional -->

- Manual deployments are able to be handled in the same anticipated environment.

### Negative Consequences <!-- optional -->

- no git push access, only pull access


### Setup config
```
    # Installed pyenv virtualenv
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv

    # Installed packages from setup.py
    python3 -m setup.py install

    # Installed packages from requirements.txt
    pip install -r requirements.txt

    # Created virtual environment with python 3.9.17
    nasa-apt-backend

    # Installed NVM
    use node 16

    # Installed aws cdk
    npm install -g aws-cdk

    # Created .env in project working dir 
    /nasa-apt
```

### Steps to Deploy (After Accessing the Instance)
- List environments, `pyenv virtualenvs`
- Activate the virtual environment, `pyenv activate nasa-apt-backend`
- Run `cdk diff`
- Deploy, `cdk deploy`


## Links <!-- optional -->

- [pyenv virtualenv docs](https://github.com/pyenv/pyenv-virtualenv/tree/cd6a51ad68efd297559de1da9a1e3f77ac3ed18f) <!-- example: Refined by [xxx](yyyymmdd-xxx.md) -->
- [install pyenv virtual env on ubuntu](https://www.liquidweb.com/kb/how-to-install-pyenv-virtualenv-on-ubuntu-18-04/)
- [install nvm on ubuntu](https://tecadmin.net/how-to-install-nvm-on-ubuntu-20-04/)

