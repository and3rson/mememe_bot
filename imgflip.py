import requests
import urllib
import re
from bs4 import BeautifulSoup


class IFApi(object):
    URL = 'https://api.imgflip.com/'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def request(self, fn, method, **kwargs):
        url = IFApi.URL + method
        # url = 'http://requestb.in/1236ku11'
        if fn in (requests.get, requests.head):
            response = fn(url + '?' + urllib.urlencode(kwargs))
        else:
            print url
            response = fn(url, data=kwargs)
        return response.json()

    def get_memes(self):
        return self.request(requests.get, 'get_memes')

    def caption_image(self, template_id, text0, text1):
        return self.request(
            requests.post, 'caption_image',
            username=self.username,
            password=self.password,
            template_id=template_id,
            text0=text0,
            text1=text1
        )

    def search_templates(self, query):
        response = requests.get(u'https://imgflip.com/memesearch?q={}'.format(query))
        doc = BeautifulSoup(response.content, 'html.parser')
        first = doc.select_one('.mt-box')
        if first:
            a = first.select_one('h3 a')
            title = a.get_text().strip()
            href = 'https://imgflip.com/{}'.format(a['href'].replace('/meme/', '/memetemplate/').rstrip('/'))
            image_url = first.select_one('img')['src']
            if image_url.startswith('//'):
                image_url = 'http:' + image_url
            return (title, href, self.get_template_id(href), image_url)
        else:
            # Nothing found :v
            return None

    def get_template_id(self, href):
        response = requests.get(href)
        matches = re.findall(r'Template ID: (\d+)', response.content)
        return matches[0]
