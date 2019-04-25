FROM ubuntu
WORKDIR /app
COPY . /app

RUN apt-get update
RUN apt-get install python3-pip --assume-yes

RUN pip3 install -r requirements.txt

RUN apt-get install -y texlive-latex-recommended

RUN apt-get install nano

# test
RUN python3 serialize.py 1 1 'test_json.json'
# RUN pdflatex ATBD_1v1.tex

