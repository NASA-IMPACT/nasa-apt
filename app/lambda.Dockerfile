FROM public.ecr.aws/lambda/python:3.8

RUN yum install -y gcc gcc-c++ make
# TODO: see if any of these packages can be removed (since moving to `latexmk` from `xelatex`), 
# in order to reduced deployment pacakge size as well as install time
RUN yum install -y\
    texlive-pdftex texlive-latex-bin texlive-texconfig* texlive-latex* texlive-metafont* \
    texlive-cmap* texlive-ec texlive-fncychap* texlive-pdftex-def texlive-fancyhdr* \
    texlive-titlesec* texlive-multirow texlive-framed* texlive-wrapfig* texlive-parskip* \
    texlive-caption texlive-ifluatex* texlive-collection-fontsrecommended texlive-lm* \
    texlive-collection-latexrecommended texlive-collection-xetex \
    libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel \
    wget
RUN wget https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-13.noarch.rpm
RUN rpm -Uvh epel-release*rpm
RUN yum install -y texlive-lineno latexmk

RUN mkdir -p ~/Library/Fonts
RUN cp -r /usr/share/texlive/texmf-dist/fonts/opentype/public/lm-math/latinmodern-math.otf   ~/Library/Fonts/
RUN cp -r /usr/share/texlive/texmf-dist/fonts/ /usr/share/fonts/

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
