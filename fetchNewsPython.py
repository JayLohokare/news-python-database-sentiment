import requests
import json
import random
from newspaper import Article
import xlrd
import pandas as pd
import numpy as np
import random

excelLocation = "Book1.xlsx"
wb = xlrd.open_workbook(excelLocation)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

def getArticleContent(url):
    article = None
    article = Article(url)
    article.download()
    article.parse()
    return article.text
	

from pymongo import MongoClient
client = MongoClient('mongodb://root:LCl67MkFgRqV@18.208.219.105', 27017)
db = client['uptick_news_database']
collection = db.news

for i in range(1, sheet.nrows):
	coinName = sheet.cell_value(i, 0)
	searchKey = sheet.cell_value(i, 2)
	APIKey = sheet.cell_value(i, 1)
	baseURL = 'https://newsapi.org/v2/everything?sortBy=publishedAt&apiKey=' + APIKey + '&q=' + searchKey 

	if sheet.ncols > 2:
		for k in range(3, sheet.ncols):
			parameter = sheet.cell_value(0, k)
			value = sheet.cell_value(i, k)
			appendToURL = '&' + parameter + '=' + value
			baseURL += appendToURL

	response = requests.get(baseURL)
	jsonVal = response.json()
	articlesTemp = jsonVal['articles']
	counter = 0

	for j in range(len(articlesTemp)):
		try:
			url = articlesTemp[j]['url']
			publishedAt = articlesTemp[i]['publishedAt']
			title = articlesTemp[j]['title']
			description = articlesTemp[i]['description']
			author = articlesTemp[j]['author']
			image = articlesTemp[j]['urlToImage']
			content = getArticleContent(url).strip()
			source = articlesTemp[j]['source']
			searchKey = searchKey

			content = content.lower()
			content = content.replace("\n", "")
			content = content.replace("\'", "")

			tempDict = {}
			tempDict['url'] = url
			tempDict['publishedAt'] = publishedAt
			tempDict['title'] = title
			tempDict['description'] = description
			tempDict['author'] = author
			tempDict['content'] = content
			tempDict['coin'] = coinName
			tempDict['sentiment'] = 0
			tempDict['relevance'] = 0
			tempDict['image'] = image
			tempDict['source'] = source
			tempDict['searchKey'] = searchKey

			searchDict ={}
			searchDict['url'] = url
			searchDict['coin'] = coinName

			if content != "":
				counter += 1
				collection.update_one(searchDict, {"$set":tempDict})
		except:
			print ("Error")
			continue
			