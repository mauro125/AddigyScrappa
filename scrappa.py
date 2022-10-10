import json
import requests
import time

from slack_token import *

import logging
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Retrieving message from Slack
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=slack_token_code)
logger = logging.getLogger(__name__)
# Store conversation history
conversation_history = []
# ID of the channel you want to send the message to
channel_id = "C03PMAFFK50"

try:
    # Call the conversations.history method using the WebClient
    # conversations.history returns the first 100 messages by default
    # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
    result = client.conversations_history(channel=channel_id)

    conversation_history = result["messages"]
    print(conversation_history)
    # Print results
    logger.info("{} messages found in {}".format(len(conversation_history), id))

except SlackApiError as e:
    logger.error("Error creating conversation: {}".format(e))

slack_channel = '#general'
comments = set()


# def post_message_to_slack(text, blocks):
def post_message_to_slack(query):
    postDateCreation = ''
    blocks = []
    urlToGetPosts = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=1"
    r = requests.get(urlToGetPosts)
    data = json.loads(r.text, strict=False)

    # Reversing the data returned so the latest message will post last
    count = len(data['data']) - 1
    for item in reversed(data['data']):
        # for item in reversed(data['data'][count]):
        if data['data'][count]['permalink'] not in comments:
            print('not in set adding new comment')
            print(data['data'][count]['permalink'])
            comments.add(item['permalink'])
            print(count, "__", item['permalink'])

            post_created_date = time.strftime('%b %d %Y %H:%M%p',
                                              time.localtime(data['data'][count]['created_utc']))
            print(post_created_date)
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
                                "text": "Acknowledged"
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
            postDateCreation = data['data'][count]['created_utc']
            # post_message_to_slack(text)
        else:
            print('no new posts')
        # count += 1
        count -= 1

    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token_code,
        'channel': slack_channel,
        'text': postDateCreation,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


def get_messages_from_slack():
    return requests.get('https://slack.com/api/conversations.history', {
        'token': 'xoxp-3788761613207-3803299958707-3816032296929-7ec486d965edb3afc2311f02c4302ca9',
        'channel': 'C03PMAFFK50',
        'limit': 1000,
        # 'Authorization': slack_token_code
    }).json()

# messages = get_messages_from_slack()
# print(messages)

# query = "addigy"
# # url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
# # url = f"https://api.pushshift.io/reddit/submission/search/?q={query}"
# # r = requests.get(url)
#
# data = json.loads(r.text, strict=False)
# print(r.text)
# print('\n\nfirstdata')
# print(data)
#
# urlInfo = data['data'][0]['permalink']
# print(urlInfo)
# postUrl = f"https://www.reddit.com{urlInfo}"

userInput = -1

while userInput != '5':
    print("\n\nenter 1 to check for new posts and comments")
    userInput = input('enter choice: ')
    if userInput == '1':
        # count = 0
        query = "addigy"
        # url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
        # url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
        # url = f"https://api.pushshift.io/reddit/submission/search/?q={query}&sort=asc"
        # url = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=2"
        # r = requests.get(url)
        #
        # data = json.loads(r.text, strict=False)
        # # data = data['data'].reverse()
        # # reverseData = reversed(data['data'])
        #
        # count = len(data['data']) - 1
        # for item in reversed(data['data']):
        #     # for item in reversed(data['data'][count]):
        #     if data['data'][count]['permalink'] not in comments:
        #         print('not in set adding new comment')
        #         print(data['data'][count]['permalink'])
        #         comments.add(item['permalink'])
        #         print(count, "__", item['permalink'])
        #
        #         post_created_date = time.strftime('%b %d %Y %H:%M%p',
        #                                           time.localtime(data['data'][count]['created_utc']))
        #         print(post_created_date)
        #         post_title = data['data'][count]['title']
        #         url_of_post = data['data'][count]['url']
        #         user_name = data['data'][count]['author']
        #         if data['data'][count]['subreddit_id'] is not None:
        #             sub_reddit = f"r/{data['data'][count]['subreddit']}"
        #         else:
        #             sub_reddit = 'no info available'
        #
        #         blocks = [
        #             {
        #                 "type": "section",
        #                 "text": {
        #                     "type": "mrkdwn",
        #                     "text": f"A new Reddit mention:\n*<{url_of_post}|{post_title}>*"
        #                 }
        #             },
        #             {
        #                 "type": "section",
        #                 "fields": [
        #                     {
        #                         "type": "mrkdwn",
        #                         "text": f"*User Name:*\nu/{user_name}"
        #                     },
        #                     {
        #                         "type": "mrkdwn",
        #                         "text": f"*Sub-reddit:*\n{sub_reddit}"
        #                     },
        #                     {
        #                         "type": "mrkdwn",
        #                         "text": "*Type:*\nPost\n"
        #                     },
        #                     {
        #                         "type": "mrkdwn",
        #                         "text": f"*When:*\n{post_created_date}\n"
        #                     },
        #                 ]
        #             },
        #             {
        #                 "type": "actions",
        #                 "elements": [
        #                     {
        #                         "type": "button",
        #                         "text": {
        #                             "type": "plain_text",
        #                             # "emoji": true,
        #                             "text": "Acknowledged"
        #                         },
        #                         "style": "primary",
        #                         "value": "click_me_123"
        #                     },
        #                     {
        #                         "type": "button",
        #                         "text": {
        #                             "type": "plain_text",
        #                             # "emoji": true,
        #                             "text": "Deny"
        #                         },
        #                         "style": "danger",
        #                         "value": "click_me_123"
        #                     }
        #                 ]
        #             }
        #         ]
        #         text = data['data'][count]['created_utc']
    post_message_to_slack(query)
    # else:
    # print('no new posts')
    # count += 1
    # count -= 1
    print(comments)
