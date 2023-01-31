"""A Python module to interact with Looker Community using InsidedAPI
Available functions:
    - initialize an API object (auth)
    - post a new article (POST)
    - edit an article (PATCH)
    - get information about an article (GET)
    - get information about an user (GET)
"""

import json
import requests
    
class InsidedApi(object):          
    def __init__(self, host, config_file):
        with open(config_file) as f:
            credentials = json.load(f)
        self.host = host
        self.credentials = credentials       
        self.session = requests.Session()
        self.auth()
    
    def auth(self):
        url = f"{self.host}/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = self.credentials
        r = self.session.post(url,data=data,headers=headers)
        access_token = r.json()["access_token"]
        headers = {'Authorization': 'Bearer ' +  access_token}
        self.headers = headers
        self.session.headers.update(headers)
        
    def get_user(self, user_id) -> json:
        """Get information about the user_id"""
        url = f"{self.host}/user/{user_id}"
        r = self.session.get(url,headers=self.headers)
        return r.json()
        
    def create_article(self, authorId, article: dict) -> int:
        """Create an article draft in Looker Community
        
        Minimal requirement for an article
        article = {
            "title": "This is an interesting article",
            "content" : "This is the content of the article",
            "categoryId": 1
        }
        """
        url = f"{self.host}/v2/articles/create"
        params = {"authorId": authorId}
        r = self.session.post(
            url,
            headers=self.headers,
            params=params,
            data=json.dumps(article))
        print(r.headers["Location"])
        articleId = r.headers["Location"].rsplit("/",1)[1] #r.headers = /v2/articles/2936
        return articleId
    
    def publish_article(self,articleId:int,moderatorId:int) ->int:
        articleId = articleId
        url = f"{self.host}/v2/articles/{articleId}/publish"
        params = {"moderatorId": moderatorId}
        r = self.session.post(
            url,
            headers=self.headers,
            params = params
        )
        return r.status_code
        
