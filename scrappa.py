import json
import requests

from slack_token import *

slack_token = slack_token_code
slack_channel = '#general'
comments = set()


# def post_message_to_slack(text, blocks):
def post_message_to_slack(text):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


# Define Your Query
# query = "verrakoooo"
# query = "000000ortencialulusss"
query = "aasdfasdfdfasdfas1222323"
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
        query = "addigy"
        # url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
        # url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
        url = f"https://api.pushshift.io/reddit/submission/search/?q={query}"
        r = requests.get(url)

        data = json.loads(r.text, strict=False)
        for item in data['data']:
            if data['data'][count]['permalink'] not in comments:
                print('not in set adding new comment')
                print(data['data'][count]['permalink'])
                comments.add(item['permalink'])
                print(count, "__", item['permalink'])

                postTitle = data['data'][count]['title']
                urlInfo = data['data'][count]['permalink']
                print(urlInfo)
                postUrl = f"https://www.reddit.com{urlInfo}"

                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"A new Reddit post has been made:\n*<{postUrl}|{postTitle}>*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Type:*\nComputer (laptop)"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*When:*\nSubmitted Aut 10"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Last Update:*\nMar 10, 2015 (3 years, 5 months)"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Reason:*\nAll vowel keys aren't working."
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Specs:*\n\"Cheetah Pro 15\" - Fast, really fast\""
                            }
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
                slack_message = str(count) + "__" + item['permalink']

                # post_message_to_slack(slack_message, blocks)
                post_message_to_slack(slack_message)
            else:
                print('no new posts')
            count += 1
        print(comments)
