import sys
import requests

params = {
    "source_url": sys.argv[1],
    "alias_url": sys.argv[2]
}

response = requests.post("https://goto-link.herokuapp.com/register", data=params)
print(str(response.content))