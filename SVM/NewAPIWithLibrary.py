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


def debug(string):
    if debugOn == 1:
        print (str(string) + '\n')

#Get time from comman line arguments
lookUpTime = int(sys.argv[1]) #In minutes

if len(sys.argv) > 2:
    debugOn = int(sys.argv[2])
else:
    debugOn = 0

if len(sys.argv) > 3:
    printEntities = int(sys.argv[3])
else:
    printEntities = 0

#All parameters go here
domainsFile = 'domains.csv'
keysFile = 'newsKeys.csv'

mapNewsToCoinsAndNames = 'newsQuerySheet.csv'
mapNewsToCoin = 'searchTermsForCoin.csv'
language = 'en'
vectorFile = 'vector.pkl'
modelFile = 'svm.pkl'
client = MongoClient('mongodb://root:LCl67MkFgRqV@18.208.219.105', 27017)
db = client['uptick_news_database']

#Collection names
news = db.news
raw = db.raw
sentiment = db.sentiments

# In[3]:


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


def getArticleContent(url):
    try:
        article = None
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""


def getRelatedCoinsUsingEntity(content):
    doc = nlp(content)
    allOrgs = []
    for ent in doc.ents:
        if printEntities == 1:
            print (str(ent.text) +  str(ent.label_))
        if ent.label_ == "ORG":
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



def getRelatedCoinsUsingDirectMatch(content):
    content = content.strip().lower().split()
    coins = []
    
    with open(mapNewsToCoinsAndNames) as csv_file2:
        csv_reader = csv.reader(csv_file2, delimiter=',')
        for row in csv_reader:
            searchTerms = row
            areAllTermsPresent = True
            for searchTerm in searchTerms:
                if searchTerm.lower().strip() not in content:
                    areAllTermsPresent = False
                    break
            if areAllTermsPresent:
                coins.append(row[0])
    
    return coins


def getFilteredContent(url):
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
    return contentExtracted



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



#Making API call per coin
currentTime = datetime.datetime.now().isoformat()
fromTime = (datetime.datetime.now() - datetime.timedelta(minutes = lookUpTime)).isoformat()


with open(mapNewsToCoinsAndNames) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    print (csv_reader)
    for row in csv_reader:
        try:
            all_articles = []
            queryCoinName = '("' + str(row[3]).strip() + '")AND("' +  str(row[4]).strip() + '")'
            debug (queryCoinName)
            searchQuery = queryCoinName 
            
            debug (searchQuery)
            
            #Commented code to select key randomly from set of keys
            # k = random.randint(0, len(keys)-1)
            # key = keys[k]

            key = "445938e7b4214f4988780151868665cc"
            newsapi = NewsApiClient(api_key=key)

            try:
                temp_articles = newsapi.get_everything(q=searchQuery,
                                    domains= domainsCommaSeperated,
                                    language=language,
                                    from_param=fromTime,
                                    to=currentTime,
                                    )
            except:
                continue
                
            all_articles = temp_articles['articles']
            debug (all_articles)

            for j in range(len(all_articles)):
                url = all_articles[j]['url']
                contentExtracted = getFilteredContent(url)
                content = all_articles[j]['content']

                if content != "":
                    #Query parameters saved as a dictionary
                    query_params = {}
                    query_params['currency'] = row[0].strip()
                    query_params['currency_name'] = row[1].strip()
                    query_params['operator1'] = row[3].strip()
                    query_params['operator2'] = row[4].strip()

                    #Initiating content to be saved into MongoDB
                    tempDict = {}
                    tempDict['url'] = url
                    tempDict['publishedAt'] = all_articles[j]['publishedAt']
                    tempDict['title'] = all_articles[j]['title']
                    tempDict['description'] = all_articles[j]['description']
                    tempDict['author'] = all_articles[j]['author']
                    tempDict['contentExtracted'] = contentExtracted
                    tempDict['content'] = content
                    tempDict['urlToImage'] = all_articles[j]['urlToImage']
                    tempDict['source'] = all_articles[j]['source']
                    tempDict['language'] = language
                    tempDict['query_params'] = query_params

                    relatedCoinsUsingEntity = getRelatedCoinsUsingEntity(content)
                    relatedCoinsUsingDirectMatch = getRelatedCoinsUsingDirectMatch(content)
                    

                    #Save sentiments into news collection (Collecting all news irrespective of relevance)
                    searchDict ={}
                    searchDict['url'] = url
                    searchDict['query_params'] = query_params
                    news.update_one(searchDict, {"$set":tempDict}, upsert=True)  

                    #Add sentiment
                    tempDict['sentiment'] = getSentiment(contentExtracted)
                    tempDict['relevance'] = 0
                    sentiment.update_one(searchDict, {"$set":tempDict}, upsert=True)


                    #Saving raw relevant news into raw and sentiment collection
                    if row[0].strip() in relatedCoinsUsingEntity:
                        searchDict ={}
                        searchDict['url'] = url
                        searchDict['query_params'] = query_params
                        raw.update_one(searchDict, {"$set":tempDict}, upsert=True)

                    
                    #Debug statement (Executed only if cmd parameters are passed correctly)
                    debug (contentExtracted)
                    debug (url)
                    debug ("Related coins using entity " + str(relatedCoinsUsingEntity))
                    debug ("Related coins using direct string match " + str(relatedCoinsUsingDirectMatch))
                    
        except Exception as e: 
            print ("Encountered error ", e)
            content = ""
            all_articles = []
            tempDict = {}
            searchDict = {}
            continue               

client.close()





#modify /etc/crontab
#35 * * * * /home/ubuntu/news-python-database-sentiment/SVM/getNews.sh


 # for coin in relatedCoinsUsingDirectMatch: 
                    #     tempDict['relatedCoin'] = coin
                    #     tempDict['symbol'] = row[0].strip()
                    #     tempDict['coinName'] = row[1].strip()
                    #     tempDict['operator1'] = row[3].strip()
                    #     tempDict['operator2'] = row[4].strip()
                    #     searchDict ={}
                    #     searchDict['url'] = url
                    #     searchDict['relatedCoin'] = coin
                    #     searchDict['coinName'] = row[0].strip()
                    #     collection.update_one(searchDict, {"$set":tempDict}, upsert=True)
                        
                    # for coin in relatedCoinsUsingEntity: 
                    #     tempDict['relatedCoin'] = coin
                    #     tempDict['symbol'] = row[0].strip()
                    #     tempDict['coinName'] = row[1].strip()
                    #     tempDict['operator1'] = row[3].strip()
                    #     tempDict['operator2'] = row[4].strip()
                    #     searchDict ={}
                    #     searchDict['url'] = url
                    #     searchDict['relatedCoin'] = coin
                    #     searchDict['coinName'] = row[0].strip()
                    #     collection2.update_one(searchDict, {"$set":tempDict}, upsert=True)