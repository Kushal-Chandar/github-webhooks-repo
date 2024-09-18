# Webhooks-Repo

Store github webhooks generate by actions repo.

## Setup

- Install flask and pymongo. Make sure you have mongo db setup on your system (change connection url in app.py)
- In the root directory
```pwsh
flask run
```
- tunnel your local host to create a public url and add it to the actions repo 'custom-url'/webhook.
- you should able to see the push, pull-request and merge events at 'custom-url'/
