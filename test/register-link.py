import sys
import requests


source, destination = sys.argv[1:]

params = {
    "source": source,
    "destination": destination
}

response = requests.post("https://goto-link.herokuapp.com/register", data=params)
print(response.content)