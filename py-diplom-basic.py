import requests

with open('token.txt', 'r') as f:
    token = f.read().strip()

url = 'http://api.vk.com/method/'
version = '5.126'
