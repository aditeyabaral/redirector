# redirector

Redirector is a simple link redirecting service. Built using Flask and SQLAlchemy, it aims to provide a way to shorten and redirect links but usually fails at the former. 

# How to use Redirector?

## Creating redirecting links

Since I'm awful at making pretty interfaces, creation of redirection links can currently only take place using POST requests.

Use the following Python script to make a POST request and create your link.

```Python
import sys
import requests

params = {
    "source_url" = sys.argv[1],
    "alias_url" = sys.argv[2]
}

response = requests.post("https://goto-link.herokuapp.com/register", data=params)
print(str(response.content))
```

Execute the above script using

```bash
python3 source_url alias_url
```

Example, use
```bash
python3 https://github.com/ git
```

## Accessing redirecting links

You can access an alias link using `goto-link/alias_name`

# Why use Redirector?

* Open Source

Yup, that's the only advantage I can think of.

# Why not to use Redirector?

* The alias links may not be always shorter because of the size of the link prefix
* Creation of alias links is tedious (for now)

It is not as bad as it sounds though.

# How to contribute to Redirector?

A pretty interface to create alias links would be a good starting point. 

# Why did I make a link redirecting service?

Honestly, even I do not know why this exists.
