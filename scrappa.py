from slack_token import *
import json
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
time_stamp_of_reddit_message = set()


# Store conversation history
def get_reddit_time_stamp_from_messages_in_slack():
    # conversation_history = []
    # ID of the channel you want to send the message to
    channel_id = "C03PMAFFK50"

    try:
        limit = 1
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id, limit=limit)

        conversation_history = result["messages"]
        # If a message is not made by the bot, skip it since only bot message will have the reddit post timestamp
        for message in conversation_history:
            # only thing I found unique to distinguish messages
            if message["blocks"][0]["type"] == 'section':
                time_stamp_of_reddit_message.add(message['text'])
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


slack_channel = '#general'


def get_posts_from_pushshift(url):
    r = ''
    while True:
        try:
            # Pushshift API rate limit is 60 requests per minute(1 request per second)
            # Adding sleep to avoid hitting the limit
            time.sleep(2)
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


def new_post_to_slack(query):
    get_reddit_time_stamp_from_messages_in_slack()
    url_to_get_posts = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=2"
    data = get_posts_from_pushshift(url_to_get_posts)

    # Reversing the data returned so the newest message will post last
    i = len(data['data']) - 1
    for _ in reversed(data['data']):
        if str(data['data'][i]['created_utc']) not in time_stamp_of_reddit_message:
            post_created_date = time.strftime('%b %d %Y %I:%M%p',
                                              time.localtime(data['data'][i]['created_utc']))
            post_title = data['data'][i]['title']
            url_of_post = data['data'][i]['full_link']
            user_name = data['data'][i]['author']
            if data['data'][i]['subreddit_id'] is not None:
                sub_reddit = f"r/{data['data'][i]['subreddit']}"
            else:
                sub_reddit = 'no info available'
            DAY = 86400
            t = time.time() - 30 * DAY
            url_to_get_user_statistics = f"https://api.pushshift.io/reddit/submission/search/?author={user_name}&q={query}&after={int(t)}"
            user_data = get_posts_from_pushshift(url_to_get_user_statistics)
            frequency_of_posts = len(user_data['data'])

            if frequency_of_posts > 1:
                frequency_of_posts_str = f"u/{user_name} has made {frequency_of_posts} posts mentioning the Keyword: *" + \
                                   query.replace('\"', '').capitalize() + "*"
            elif frequency_of_posts == 0:
                frequency_of_posts_str = f"u/{user_name} has made no posts mentioning" + " the Keyword: *" + \
                                   query.replace('\"', '').capitalize() + "* (this is older than 1 month)"
            else:
                frequency_of_posts_str = f"u/{user_name} has made {frequency_of_posts} post mentioning the Keyword: *" + \
                                   query.replace('\"', '').capitalize() + "*"
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
                    ]
                },
                {
                    "type": "section",
                    "fields": [
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
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Frequency of posts:*\nIn the last 30 days, {frequency_of_posts_str}"
                    }
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
            # sending reddit post time stamp to slack, so we can later check if the post has already been posted
            post_date_creation = data['data'][i]['created_utc']

            requests.post('https://slack.com/api/chat.postMessage', {
                'token': slack_token_code,
                'channel': slack_channel,
                'text': post_date_creation,
                'blocks': json.dumps(blocks) if blocks else None
            }).json()
        else:
            print('no new posts')
        i -= 1


user_input = -1

while user_input != '5':
    print("\n\nenter 1 to check for new posts and comments")
    user_input = input('enter choice: ')
    if user_input == '1':
        queries = ['addigy', 'mosyle', 'kandji', 'Jamf', "\"jumpcloud\""]
    # iterating through the queries
    for query in queries:
        new_post_to_slack(query)
    get_reddit_time_stamp_from_messages_in_slack()
