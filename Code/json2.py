import json

info = json.loads(open('defaults.json').read())
t = info['timeInterval']
print(t,type(t))
t = info['numberRequests']
print(t,type(t))