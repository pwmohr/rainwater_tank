import urllib.request

import urllib.request
with urllib.request.urlopen('http://192.168.0.40') as response:
   html = response.read()

print(html)