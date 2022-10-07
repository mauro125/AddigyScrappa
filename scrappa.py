import json
import requests
import time

from slack_token import *

slack_token = slack_token_code
slack_channel = '#general'
comments = set()


# def post_message_to_slack(text, blocks):
def post_message_to_slack():
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


query = "addigy"
# url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
url = f"https://api.pushshift.io/reddit/submission/search/?q={query}"
r = requests.get(url)

data = json.loads(r.text, strict=False)
print(r.text)
print('\n\nfirstdata')
print(data)

urlInfo = data['data'][0]['permalink']
print(urlInfo)
postUrl = f"https://www.reddit.com{urlInfo}"

userInput = -1

while userInput != '5':
    print("\n\nenter 1 to check for new posts and comments")
    userInput = input('enter choice: ')
    if userInput == '1':
        count = 0
        query = "aasdfasdfdfasdfas1222323"
        # url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
        # url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
        url = f"https://api.pushshift.io/reddit/submission/search/?q={query}&sort=asc"
        r = requests.get(url)

        data = json.loads(r.text, strict=False)
        for item in data['data']:
            if data['data'][count]['permalink'] not in comments:
                print('not in set adding new comment')
                print(data['data'][count]['permalink'])
                comments.add(item['permalink'])
                print(count, "__", item['permalink'])

                post_created_date = time.strftime('%b %d %Y %H:%M%p',
                                                  time.localtime(data['data'][count]['created_utc']))
                post_title = data['data'][count]['title']
                url_of_post = data['data'][count]['url']
                user_name = data['data'][count]['author']
                if data['data'][count]['subreddit_id'] is not None:
                    sub_reddit = f"r/{data['data'][count]['subreddit']}"
                else:
                    sub_reddit = 'no info available'

                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"A new Reddit mention:\n*<{url_of_post}|{post_title}>*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*User Name:*\nu/{user_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Sub-reddit:*\n{sub_reddit}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Type:*\nPost\n"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*When:*\n{post_created_date}\n"
                            },
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    # "emoji": true,
                                    "text": "Approve"
                                },
                                "style": "primary",
                                "value": "click_me_123"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    # "emoji": true,
                                    "text": "Deny"
                                },
                                "style": "danger",
                                "value": "click_me_123"
                            }
                        ]
                    }
                ]
                post_message_to_slack()
            else:
                print('no new posts')
            count += 1
        print(comments)
