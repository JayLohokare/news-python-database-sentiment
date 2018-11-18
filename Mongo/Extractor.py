
# coding: utf-8

# In[6]:


#!python -m pip install pymongo


# In[35]:


import requests
import pandas as pd
import numpy as np
import math
import time
import pickle
import pymongo


# In[36]:


cryptocurrency = pd.read_csv("./doc/News API Queries .csv")


# ## Data Extraction

# In[58]:


def getCryptocurrenciesNews(row,from_,to_):
    json_list = []
    news_api_request = "https://newsapi.org/v2/everything?language=en&q=({})AND('{}')&from={}&to={}&pageSize={}&page={}&sortBy=relevancy&domains=techradar.com,nulltx.com,ccn.com,hackernoon.com,seekingalpha.com,newsbtc.com,coindesk.com,medium.com,thenextweb.com,bitcoinist.com,marketwatch.com,mashable.com,zdnet.com,prnewswire.com,thehackernews.com,fortune.com,apnews.com,bitcoinmagazine.com,cointelegraph.com,businessinsider.com,dailyfx.com,reuters.com,techcrunch.com,medium.com,bloomberg.com,dailyfintech.com,99bitcoins.com,digitaltrends.com,crypto-reporter.com,bitcoin.com,ethereumworldnews.com&apiKey={}"
    apikey = ["445938e7b4214f4988780151868665cc"]
    query = {"currency":row.currency,"currency_name":row.currency_name,"operator1":row.operator_query,"operator2":row.operator_and}
    k = 0
    m = 100
    response = requests.get(news_api_request.format(row.operator_query,row.operator_and,from_,to_,1,1,apikey[k]))
    total = response.json().get("totalResults")
    pages = math.ceil(total/m)
    #print(total)
    for n in np.arange(1,pages+1):
        response = requests.get(news_api_request.format(row.operator_query,row.operator_and,from_,to_,m,n,apikey[k]))
        response = response.json()
        
        for article in response.get("articles"):
            article["query_param"] = query
            json_list.append(article)    
    return json_list


# In[42]:


articles = []
for i,xdata in cryptocurrency.iterrows():
    result = getCryptocurrenciesNews(xdata,"2018-10-11","2018-11-11")
    articles = articles + result


# # Data fetching

# In[46]:


articles_dict = articles


# In[51]:


def insertDataMongodb(data):  
    client = pymongo.MongoClient('mongodb://root:LCl67MkFgRqV@18.208.219.105/?retryWrites=true', 27017)
    news_data = client.historical_news_database
    news = news_data.news_articles
    news.insert_many(data)    


# In[52]:


insertDataMongodb(articles_dict)

