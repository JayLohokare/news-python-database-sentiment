rm -r /home/ubuntu/newLog.log
cd /home/ubuntu/news-python-database-sentiment/SVM/
python3 -W ignore NewAPIWithLibrary.py 1000 1 1 1 &>> /home/ubuntu/newLog.log
