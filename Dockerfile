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
    python3 -m spacy download en && \
    locale-gen "en_US.UTF-8" && \
    dpkg-reconfigure locales

ADD ./SentimentUptick/news-python-database-sentiment /home/ubuntu/news-python-database-sentiment

WORKDIR /home/ubuntu/news-python-database-sentiment/SVM/

RUN python3 NewAPIWithLibrary.py 1000 0 0