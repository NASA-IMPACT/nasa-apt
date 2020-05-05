This folder contains the files which compose the `tex` Docker image, which converts the information received via the json dump from the database into a .tex file.

## Directory

base_commands.sh are executed at the creation of the docker container to install the needed python libraries, including `awscli` and those enumerated in `requirements.txt`.

entrypoint.sh includes the commands which will be executed when the container is spun up. It copies in the required files from S3, calls the python code to create the TeX file, and copies output to s3 so the other containers can use it.

serialize.py contains the python code used to translate the information in the JSON file into a TeX file and corresponding BibTeX file.

ATBD.tex provides the TeX template which will be modified to include the formatted data by serialize.py.
 
