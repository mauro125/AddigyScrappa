import json
import time
from pprint import pprint

import requests


def get_posts_from_pushshift(url):
    r = ''
    while True:
        try:
            # Pushshift API rate limit is 60 requests per minute(1 request per second)
            # Adding sleep to avoid hitting the limit
            time.sleep(1)
            r = requests.get(url)
            if r.status_code != 200:
                print("error code", r.status_code)
                time.sleep(7)
                continue
            else:
                break
        except Exception as e:
            print("error: ", e)
            time.sleep(5)
            continue
    return json.loads(r.text, strict=False)


query = 'addigy'
size = 2
url_to_get_comments = f"https://api.pushshift.io/reddit/comment/search/?q={query}&size={size}"
data = get_posts_from_pushshift(url_to_get_comments)

pprint(data)

print("\n\n\n")

# this is how you would access what you want, change 0 to i (or whatever) to use in a loop
print(data['data'][0]['created_utc'])
print(data['data'][0]['subreddit_name_prefixed'])
