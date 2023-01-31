"""A Python script to:  
(1) scrape the content of Looker blogposts from Internet Archieve using BeautifulSoup
(2) edit, and save the content to a CSV file
(3) post the formatted content to Looker Community using inSided API
The logic in the script is customized to Looker, and can serve as a template for similar projects.

Author: lantrann@
Last modified: March 2022
"""

import requests
from bs4 import BeautifulSoup
from insided import InsidedApi
import time

def main():
    """The main workflow, returning two csv files:
    (1): master.csv, storing all metadata of posts (content, author, etc.)
    (2): errors.csv, storing all URLs that can be parsed from Internet Archieve
    """
    urls = get_url(file="link.csv")
    for url in urls:
        time.sleep(3) # avoid API timeout
        try: 
            data = transform_content(url)
            article_id = post_to_community(data=data)
            with open("master.csv", "a") as f:
                f.write("%s,%s,%s,%s,%s,%s\n"%({article_id},{data["url"]},{data["title"]}, 
                        {data["author"]}, {data["date"]}, {data["content"]}))
        except:
            with open("errors.csv", "a") as f:
                f.write("%s\n"%(url))

def get_url(file) -> list:
    """Read from a file to retrieve all URL"""
    with open(file, "r") as f:
        urls = f.read().splitlines()
    return urls

def transform_content(url: str) -> dict:
    """Get article from Internet Archive URL, parse and edit content
    using Beautiful Soup. Data is then packaged into a dictionary, 
    consisting of title, author, date, and formatted content."""

    r = requests.get(url)
    if r.status_code == 200:        
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find('div', {'class' : 'blog-post'})
            
        # Get text for title, author, date from BeautifulSoup's tag object 
        title = content.find('h1', {'class': 'top--0'}).get_text(strip=True)
        author = content.find('p',{'class': 'author bottom--0'}).get_text(strip=True).split(",",1)[0] #split to remove title and space
        date = content.find('p',{'class': 'date'}).get_text(strip=True)
            
        # Remove link and images since these links are dead
        for atag in content.find_all('a', {'href': True}):
            if not atag['href'].startswith('https://looker.com'):
                atag.extract()
        for imgtag in content.find_all('img', {'src': True}):
            imgtag.extract()

        # Remove the first 15 lines (title, authors), and the last 6 lines (footer)      
        content_raw = str(content).split("\n",15)[15].rsplit("\n",6)[0]

        # Format content, and add disclaimer to the post         
        disclaimer = f'<section class="callout callout-gray"><p>This content, written by {author}, was initially posted in Looker Blog on {date}. The content is subject to <a href="https://community.looker.com/knowledge-drops-1021/important-supportability-of-knowledge-drops-23344" rel="noreferrer" target="_blank"><u>limited support.</u></a></section><p></p><p></p>'
        content = disclaimer + content_raw
       
        data = {
            "url": url,
            "title": title,
            "author": author,
            "date": date,
            "content" : content
        }        
        return data
        
def post_to_community(data:dict)->int:
    """ Post to Looker Community using methods from the `insided.py` module. 
    Read README.md to see required parameters. Return the article id of the 
    newly posted article"""

    authorId = 12382 #https://community.looker.com/members/department-of-customer-love-12382
    moderatorId = 7192 #https://community.looker.com/members/lan-7192
    categoryId = 1027 #https://community.looker.com/blog-archives-1027
    article = {
        "title": data["title"],
        "content" : data["conctent"],
        "categoryId": categoryId
    }
    article_id = insided.create_article(authorId=authorId,article=article)
    insided.publish_article(articleId=article_id, moderatorId=moderatorId)
    return article_id

# Initialize an API object. Read README for config file parameters
insided = InsidedApi(host="https://api2-us-west-2.insided.com",
                     config_file="tse/migrate_blog/insided.json")

main()
