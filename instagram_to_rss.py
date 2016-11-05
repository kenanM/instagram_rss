"""
This script turns someones Instagram page into an RSS feed.

Further reading on the RSS spec: https://cyber.harvard.edu/rss/rss.html

"""
import argparse
import json
import os
import re
import requests
from datetime import datetime

from bs4 import BeautifulSoup
from jinja2 import Template

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'template.rss')
TITLE_LENGTH = 50

parser = argparse.ArgumentParser()
parser.add_argument('usernames', nargs='*')
parser.add_argument('--out', default='instagram/')


class FeedItem(object):
    def __init__(self, code, thumbnail_src, caption, timestamp):
        self.code = code
        self.thumbnail_src = thumbnail_src
        self.caption = caption
        self.date = datetime.fromtimestamp(timestamp)

    @property
    def title(self):
        if len(self.caption) <= TITLE_LENGTH:
            return self.caption or 'Untitled'
        shorter_caption = self.caption[:TITLE_LENGTH - 3]
        return '%s...' % shorter_caption

    @property
    def link(self):
        return 'https://www.instagram.com/p/{}/'.format(self.code)

    @property
    def pub_date(self):
        """ Generates a date formatted to RFC 2"""
        return self.date.strftime('%a, %d %b %Y %H:%m:%S GMT')


def generate_feed(username, out_dir):
    response = requests.get('https://instagram.com/{}/'.format(username))
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text)
    node = soup.find(text=re.compile('^window._sharedData'))
    stripped_node = node.lstrip('window._sharedData = ').rstrip(';')
    data = json.loads(stripped_node)
    items = []
    for node in data['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
        items.append(
            FeedItem(
                node['code'],
                node['thumbnail_src'],
                node.get('caption', ''),
                node['date'],
            )
        )

    print 'Found {} items for {}'.format(len(items), username)
    template = Template(open(TEMPLATE_PATH).read(), autoescape=True)
    with open(os.path.join(out_dir, username), 'w+') as out_file:
        out_file.write(
            template.render(username=username, items=items).encode('utf-8'))

if __name__ == '__main__':
    args = parser.parse_args()
    for username in args.usernames:
        generate_feed(username, args.out)
