import sys
import requests


destination = sys.argv

params = {
    "destination": destination
}

response = requests.post("https://goto-link.herokuapp.com/delete", data=params)
print(response.content)