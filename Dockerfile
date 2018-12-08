FROM ubuntu:16.04

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-setuptools python3-pip && \
    pip3 install pymongo  && \
    pip3 install newsapi-python && \
    pip3 install newspaper3k && \
    pip3 install pandas && \
    pip3 install sklearn && \
    pip3 install spacy && \
    python3 -m spacy download en

ADD news-python-database-sentiment news-python-database-sentiment
ADD newLog.log newLog.log

WORKDIR /home/ubuntu/news-python-database-sentiment/SVM/

RUN ls

RUN chmod +x /home/ubuntu/news-python-database-sentiment/SVM/dockerRun.sh

RUN sh /home/ubuntu/news-python-database-sentiment/SVM/dockerRun.sh