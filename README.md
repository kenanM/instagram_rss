# instagram_rss
Generate RSS feed's from Instagram pages. 

A simple script design to be called by cron that generates rss feeds for an instagram user.

Call it like this `python instagram_to_rss.py account1 account2 account3 --out /var/www/static/instagram/`

Requires BeautifulSoup4 and Jinja2.
