import urllib.request
import re

url = 'https://www.youtube.com/@BumbleBabu/live'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

match = re.search(r'"videoId":"([^"]+)"', html)
if match:
    print('Found video ID:', match.group(1))
else:
    print('Not found')
