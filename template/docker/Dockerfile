FROM ubuntu
WORKDIR /app
COPY . /app

RUN apt-get update
RUN apt-get install python3-pip --assume-yes

RUN pip3 install -r requirements.txt

RUN apt-get install -y texlive-latex-recommended

# test
RUN pdflatex ATBD_1v1.tex

