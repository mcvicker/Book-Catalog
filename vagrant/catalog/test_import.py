import json

description = json.loads(
    open('neuromancer.json', 'r').read())["items"][0]['volumeInfo']['description']
print description