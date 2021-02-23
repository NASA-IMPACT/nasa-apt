FROM public.ecr.aws/lambda/python:3.7

RUN yum install -y gcc gcc-c++ make

RUN yum install -y\
    texlive texlive-latex texlive-xetex texlive-collection-latexrecommended\
    yum install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel

RUN rm -rf /var/lib/apt/lists/*

ENV LANG en_US.utf8

WORKDIR ./

COPY README.md ./README.md
COPY app/ ./app/
COPY setup.py ./setup.py


RUN pip install --upgrade pip
RUN pip install . "mangum>=0.9.0"  --no-binary xmlsec numpy pydantic

# Reduce package size and remove useless files
#RUN cd /var/task && find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[2-3][0-9]//'); cp $f $n; done;
#RUN cd /var/task && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
#RUN cd /var/task && find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
#RUN find /var/task -type d -a -name 'tests' -print0 | xargs -0 rm -rf
#RUN rm -rdf /var/task/numpy/doc/
#RUN rm -rdf /var/task/stack

COPY lambda/handler.py ./handler.py

CMD ["handler.handler"]
