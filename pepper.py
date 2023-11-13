import requests

response = requests.get('https://www.pepper.ru/')
print(response.status_code)