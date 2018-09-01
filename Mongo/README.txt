Install CronTab
sudo apt-get install gnome-schedule
crontab -e

10 * * * * bash /home/ubuntu/.jupyter/getNews.sh


//Assumes chmod -x NAMEOFSH