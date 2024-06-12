import requests
resp = requests.post('https://textbelt.com/text', {
  'phone': '+14014772068',
  'message': 'Hello world',
  'key': '7739b4b625177ed8c64499280673ac9a15fb4ba4LNkpba5rJYiuXIkTt1n3zzYf9',
})
print(resp.json())