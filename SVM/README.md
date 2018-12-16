Code for news module of daix.io

This repo contains code to fetch real time news and save it into MongoDB + REDIS. 

NewAPIWithLibrary.py runs as cron job on AWS to write news data into DB and cache. 
Crontab calls getNews.sh which inturn calls NewAPIWithLibrary.py


Installation instruction ->
1. Crontab runs all codes as sudo, hence install all libraries as sudo (sudo pip3 install <>)

Parameters for NewAPIWithLibrary.py:
```
python3 NewAPIWithLibrary.py <Number of hours to look up> <debugOn> <printEntities>
```

Pass debugOn = 1 to print all values fetched and logs. getNews.sh routes all print to newLog.log file
printEntities = 1 will print all named entities extracted from the news fetched from newsapi.org

crontab takes absolute path -> Runs /ubuntu/home/news-python-database-sentiment/SVM/getNews.sh
The getNews.sh is configured to work correctly following this convention. 

NewAPIWithLibrary.py uses following CSVs for filtering newsapi calls ->
1. newsQuerySheet.csv -> Gets names of coins, coin symbol, (operators1)AND(operator2) are passed to q of newsapi.
2. domains.csv -> Domains passed to newsapi call 

The code saves all news fetched in uptick_news_database database.
1. Raw news are stored in 'news' collection
2. 'sentiment' collection stores raw news + sentiments

REDIS contains multiple queues containing latest 100 news
1. All news fetched are stored in REDIS with Key = url, value = dictionary (JSON news)
2. Similarly, COIN_NAME + url is also used as key for all articles with value being JSON news
3. 'news' queue contains REDIS keys of format URL for latest 100 news
4. There are queues per coin (Queue name = <COIN_SYMBOL>) storing keys of format COIN_NAME + url