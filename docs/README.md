# AUTH
```python
client_id = '5362854'
client_secret = '4RP2ARy6KVqZWZNpkVAw'
token_url = 'https://oauth.vk.com/access_token'

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token_dict = oauth.fetch_token(token_url=token_url, 
                               client_id=client_id,
                               client_secret=client_secret)
                               
access_token = token_dict.get('access_token')
```

# METHOD
https://api.vk.com/method/'''METHOD_NAME'''?'''PARAMETERS'''&access_token='''ACCESS_TOKEN'''
