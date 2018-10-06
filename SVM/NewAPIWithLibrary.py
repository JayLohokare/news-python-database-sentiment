import csv
import requests
import json
import random
from newspaper import Article
from newsapi.newsapi_client import NewsApiClient
import datetime
from pymongo import MongoClient

import pickle as p
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt


domainsFile = 'domains.csv'
keysFile = 'newsKeys.csv'
lookUpTime = 1000 #In minutes
mapNewsToCoin = 'searchTermsForCoin.csv'
language = 'en'
vectorFile = 'vector.pkl'
modelFile = 'svm.pkl'

client = MongoClient('mongodb://root:LCl67MkFgRqV@18.208.219.105', 27017)
db = client['uptick_news_database']
collection = db.news2


namesList = []
domainsList = []
with open(domainsFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        domainsList.extend(row)
        
domainsCommaSeperated = ','.join(domainsList)



keys = []
with open(keysFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        keys.append(row[0])

k = random.randint(0, len(keys)-1)
key = keys[k]


all_articles = []

currentTime = datetime.datetime.now().isoformat()
fromTime = (datetime.datetime.now() - datetime.timedelta(minutes = lookUpTime)).isoformat()

newsapi = NewsApiClient(api_key=key)
temp_articles = newsapi.get_everything(q='crypto',
                                    domains= domainsCommaSeperated,
                                    language=language,
                                    from_param=fromTime,
                                    to=currentTime,
                                    )
all_articles.extend(temp_articles['articles'])   


def getArticleContent(url):
    try:
        article = None
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""



def getRelatedCoins(content):
    content = content.split()
    coins = []
    
    with open(mapNewsToCoin) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            for i in row:
                i = i.lower()
                if i in content:
                    coins.append(row[0])
                    break
    return coins


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
	

for j in range(len(all_articles)):
    url = all_articles[j]['url']
    content = getArticleContent(url).strip()
    content = content.lower()
    content = content.replace("\n", "")
    content = content.replace("\'", "")

    if content != "":
        tempDict = {}
        tempDict['url'] = url
        tempDict['publishedAt'] = all_articles[j]['publishedAt']
        tempDict['title'] = all_articles[j]['title']
        tempDict['description'] = all_articles[j]['description']
        tempDict['author'] = all_articles[j]['author']
        tempDict['content'] = content
        tempDict['image'] = all_articles[j]['urlToImage']
        tempDict['source'] = all_articles[j]['source']
        tempDict['language'] = language

        tempDict['sentiment'] = getSentiment(content)
        tempDict['relevance'] = 0

        relatedCoins = getRelatedCoins(content)

        for coin in relatedCoins: 
            tempDict['coin'] = coin
            searchDict ={}
            searchDict['url'] = url
            searchDict['coin'] = coin
            collection.update_one(searchDict, {"$set":tempDict}, upsert=True)

