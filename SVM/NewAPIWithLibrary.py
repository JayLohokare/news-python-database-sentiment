#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import requests
import json
import random
from newspaper import Article
from newsapi.newsapi_client import NewsApiClient
import datetime
from pymongo import MongoClient
import sys
import pickle as p
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier


import re
import spacy
nlp = spacy.load('en_core_web_sm')


# In[2]:

#Get time from comman line arguments
lookUpTime = sys.argv[0] #In minutes

#All parameters go here
domainsFile = 'domains.csv'
keysFile = 'newsKeys.csv'
mapNewsToCoin = 'searchTermsForCoin.csv'
language = 'en'
vectorFile = 'vector.pkl'
modelFile = 'svm.pkl'
client = MongoClient('mongodb://root:LCl67MkFgRqV@18.208.219.105', 27017)
db = client['uptick_news_database']
collection = db.news5


# In[3]:


namesList = []
domainsList = []
with open(domainsFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        domainsList.extend(row)
        
domainsCommaSeperated = ','.join(domainsList)


# In[4]:


keys = []
with open(keysFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        keys.append(row[0])


# In[ ]:





# In[5]:


def getArticleContent(url):
    try:
        article = None
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""


# In[13]:


def getRelatedCoins(content):
    doc = nlp(content)
    allOrgs = []
    for ent in doc.ents:
        print (ent.text, ent.label_)
        if ent.label_ == "ORG" or ent.label_ == "PERSON":
            allOrgs.append(ent.text.lower())
    
    coins = []
    
    allOrgs = [i.lower() for i in allOrgs]
    
    with open(mapNewsToCoin) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            for i in row:
                i = i.lower().strip()
                if i in allOrgs:
                    coins.append(row[0])
                    break
    return coins


# In[7]:


def getSentiment(content):
    content = [content]
    file = open(vectorFile, 'rb')
    vect = p.load(file)
    file.close()

    file = open(modelFile, 'rb')
    SVM = p.load(file)
    file.close()
    
    test_dtm = vect.transform(content)
    predLabel = SVM.predict(test_dtm)
    tags = ['Negative','Neutral','Positive']

    return predLabel[0]


# In[14]:


#Making single API call
# searchQuery = "cryptocurrencies"
# print (searchQuery)

# k = random.randint(0, len(keys)-1)
# key = keys[k]
# newsapi = NewsApiClient(api_key=key)

# temp_articles = newsapi.get_everything(q=searchQuery,
#                                     domains= domainsCommaSeperated,
#                                     language=language,
#                                     from_param=fromTime,
#                                     to=currentTime,
#                                     )
# all_articles = temp_articles['articles']

# for j in range(len(all_articles)):
#     url = all_articles[j]['url']
#     contentExtracted = getArticleContent(url).strip()
#     contentExtracted = contentExtracted.replace("\'", "")
#     contentExtracted = contentExtracted.split()
#     contentExtracted2 = []
#     for i in contentExtracted:
#         if i == "Advertisement" or i == "advertisement":
#             continue
#         else:
#             contentExtracted2.append(i)

#     contentExtracted = " ".join(contentExtracted2)

#     content = all_articles[j]['content']

#     if content != "":
#         tempDict = {}
#         tempDict['url'] = url
#         tempDict['publishedAt'] = all_articles[j]['publishedAt']
#         tempDict['title'] = all_articles[j]['title']
#         tempDict['description'] = all_articles[j]['description']
#         tempDict['author'] = all_articles[j]['author']
#         tempDict['contentExtracted'] = contentExtracted
#         tempDict['content'] = content

#         tempDict['image'] = all_articles[j]['urlToImage']
#         tempDict['source'] = all_articles[j]['source']
#         tempDict['language'] = language

#         tempDict['sentiment'] = getSentiment(contentExtracted)
#         tempDict['relevance'] = 0

#         relatedCoins = getRelatedCoins(contentExtracted)

#         print (contentExtracted)
#         print ("\n")
#         print (url)
#         print ("Related coins " , relatedCoins)
#         print ("\n")

#         for coin in relatedCoins: 
#             tempDict['coin'] = coin
#             searchDict ={}
#             searchDict['url'] = url
#             searchDict['coin'] = coin
#             collection.update_one(searchDict, {"$set":tempDict}, upsert=True)


# In[16]:


#Making API call per coin
currentTime = datetime.datetime.now().isoformat()
fromTime = (datetime.datetime.now() - datetime.timedelta(minutes = lookUpTime)).isoformat()

with open(mapNewsToCoin) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        all_articles = []
        queryCoinName = row[0]
        searchQuery = queryCoinName + " cryptocurrencies"
        print (searchQuery)
        
        k = random.randint(0, len(keys)-1)
        key = keys[k]
        newsapi = NewsApiClient(api_key=key)

        temp_articles = newsapi.get_everything(q=searchQuery,
                                            domains= domainsCommaSeperated,
                                            language=language,
                                            from_param=fromTime,
                                            to=currentTime,
                                            )
        all_articles = temp_articles['articles']
        print (all_articles)

        for j in range(len(all_articles)):
            url = all_articles[j]['url']
            contentExtracted = getArticleContent(url).strip()
            contentExtracted = contentExtracted.replace("\'", "")
            contentExtracted = contentExtracted.split()
            contentExtracted2 = []
            for i in contentExtracted:
                if i == "Advertisement" or i == "advertisement":
                    continue
                else:
                    contentExtracted2.append(i)

            contentExtracted = " ".join(contentExtracted2)

            content = all_articles[j]['content']

            if content != "":
                tempDict = {}
                tempDict['url'] = url
                tempDict['publishedAt'] = all_articles[j]['publishedAt']
                tempDict['title'] = all_articles[j]['title']
                tempDict['description'] = all_articles[j]['description']
                tempDict['author'] = all_articles[j]['author']
                tempDict['contentExtracted'] = contentExtracted
                tempDict['content'] = content

                tempDict['image'] = all_articles[j]['urlToImage']
                tempDict['source'] = all_articles[j]['source']
                tempDict['language'] = language

                tempDict['sentiment'] = getSentiment(contentExtracted)
                tempDict['relevance'] = 0

                relatedCoins = getRelatedCoins(contentExtracted)

                print (contentExtracted)
                print ("\n")
                print (url)
                print ("Related coins " , relatedCoins)
                print ("\n")

#                 if queryCoinName not in relatedCoins:
#                     relatedCoins.append(queryCoinName)
                    
                for coin in relatedCoins: 
                    tempDict['coin'] = coin
                    searchDict ={}
                    searchDict['url'] = url
                    searchDict['coin'] = coin
                    collection.update_one(searchDict, {"$set":tempDict}, upsert=True)


# In[9]:


test = "The race to build the best public blockchain will be won by those that would scale in line with volume. On a Sunday, a blockchain project realistically did it, though for 24 hours. Waves Platform, comprising of a digital ledger project and decentralized exchange (DEX), processed 6.1 million real-time transactions in a stress test. As it found, the network faced no disruptions or delays as the test intensified. None of the transactions on its system – undertaken by users for DEX orders, transfers, token creation, etc. – experienced any slowdown, either. The Waves blockchain, according to data provided by PYWAVES, recorded a total of 108,741 transactions. Among them, 60,933 were Mass Transfers which, per Waves blog post, are specialized transactions that can hold 100 transfer at once. “A total of 6,141,108 transfers was processed by the network, with the blockchain supporting hundreds of transactions per second at peak times,” the post claimed. The platform euphorically claimed that it was the highest number of transactions ever processed by any public blockchain. Waves NG Several blockchain projects in the crypto space are attempting to find alternatives to Bitcoin’s slow transaction confirmation periods. Ethereum was posed as a solution. But, it faced the same problem CryptoKitties – a decentralized application launched on Ethereum’s blockchain – slowed down transactions on the network. While Bitcoin has opted for third-party solutions like Lightning Network to handle the volume [temporarily], Ethereum is following a test-and-implement approach by taking in answers from its community developers. Waves, to achieve a similar goal, have implemented a tech called Waves NG that helps to scale the Waves Network by selecting miners in advance, thus minimizing latency and maximizing throughput. According to Waves’ CEO and co-founder Sasha Ivanov, the protocol’s deployment on their blockchain helped them process the record transactions. “Bitcoin processes just a few transactions per second,” he said. “Ethereum’s capacity is into double-digit tps, and a handful of other blockchains have improved on this incrementally in various ways. WAVES has implemented tech that enables a step-change in transaction volumes — not just in the lab, but in the real world, on MainNet, as these figures prove beyond doubt.” The Waves post noted that other blockchain projects had not exceeded more than 2 million transactions per day. However, a tweet from Ivanov admitted that EOS, a semi-decentralized blockchain project, had in fact executed 5 million transactions within a 24-hour period. EOS had 5.5 mil at most. — Sasha Ivanov (@sasha35625) October 23, 2018 A commentator also posted a chart from Blocktivity that suggested Waves was behind five blockchain projects concerning transaction volume. The chart later earned the “bogus” status from one of the Waves followers. Featured image from Shutterstock."


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




