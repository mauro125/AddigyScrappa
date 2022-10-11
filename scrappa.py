from slack_token import *
import json
from pprint import pprint
import requests
import time
import logging
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Retrieving message from Slack
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=slack_token_code)
logger = logging.getLogger(__name__)
timeStampOfRedditMessage = set()


# Store conversation history
def get_reddit_time_stamp_from_messages_in_slack():
    # conversation_history = []
    # ID of the channel you want to send the message to
    channel_id = "C03PMAFFK50"

    try:
        limit = 20
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id, limit=limit)

        conversation_history = result["messages"]

        for message in conversation_history:
            if message["blocks"][0]["type"] == 'section':
                timeStampOfRedditMessage.add(message['text'])
        # print(conversation_history[9]['text'])
        pprint(conversation_history)
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


slack_channel = '#general'


# def post_message_to_slack(text, blocks):
def new_post_to_slack(query):
    get_reddit_time_stamp_from_messages_in_slack()
    # postDateCreation = ''
    # blocks = []
    urlToGetPosts = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=3"
    r = requests.get(urlToGetPosts)
    data = json.loads(r.text, strict=False)

    # Reversing the data returned so the newest message will post last
    count = len(data['data']) - 1
    for item in reversed(data['data']):
        # for item in reversed(data['data'][count]):
        # if data['data'][count]['permalink'] not in comments:
        if str(data['data'][count]['created_utc']) not in timeStampOfRedditMessage:
            print('not in set adding new comment')
            print(data['data'][count]['permalink'])
            print(count, "__", item['permalink'])

            post_created_date = time.strftime('%b %d %Y %I:%M%p',
                                              time.localtime(data['data'][count]['created_utc']))
            post_title = data['data'][count]['title']
            url_of_post = data['data'][count]['full_link']
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
                        "text": "A new Reddit post mentions the keyword: *" + query.replace('\"', '').capitalize() +
                                f"*\n*<{url_of_post}|{post_title}>*"
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
                                "text": "Acknowledged"
                            },
                            "style": "primary",
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Deny"
                            },
                            "style": "danger",
                            "value": "click_me_123"
                        }
                    ]
                }
            ]
            # sending reddit post time stamp to slack, so we can later compare if the post has already been posted
            postDateCreation = data['data'][count]['created_utc']

            requests.post('https://slack.com/api/chat.postMessage', {
                'token': slack_token_code,
                'channel': slack_channel,
                'text': postDateCreation,
                'blocks': json.dumps(blocks) if blocks else None
            }).json()
        else:
            print('no new posts')
        # count += 1
        count -= 1

    # return response


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
        queries = ['addigy', 'mosyle', 'kandji', 'Jamf', "\"Manage Apple Devices\""]
        # queries = ['kandji']
        # url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
        # url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
        # url = f"https://api.pushshift.io/reddit/submission/search/?q={query}&sort=asc"
        # url = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=2"
        # r = requests.get(url)

    for query in queries:
        new_post_to_slack(query)
    get_reddit_time_stamp_from_messages_in_slack()
