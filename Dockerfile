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

RUN echo "First LS"
RUN ls


WORKDIR /home/ubuntu

ADD /news-python-database-sentiment /home/ubuntu/news-python-database-sentiment
ADD newLog.log /home/ubuntu/newLog.log

RUN echo "Second LS"
RUN ls
RUN chmod +x /home/ubuntu/news-python-database-sentiment/SVM/getNews.sh

RUN sh /home/ubuntu/news-python-database-sentiment/SVM/getNews.sh