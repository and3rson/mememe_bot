import requests
import urllib


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
