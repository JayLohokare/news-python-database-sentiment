Install CronTab
sudo apt-get install gnome-schedule
crontab -e

*/10 * * * * /home/ubuntu/getNews.sh

chmod +x NAMEOFSH

Add to crantab -e
MAILTO=jaylohokare@gmail.com

Check results 
grep CRON /var/log/syslog

//If cron logs have errors -> MTA error
sudo aptitude install postfix


//Current timestamp
date


