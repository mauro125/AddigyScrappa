from transformers import pipeline

from slack_token import *
import json
import requests
import time
import logging
import xlsxwriter
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Retrieving message from Slack
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=slack_bot_reddit)
logger = logging.getLogger(__name__)
time_stamp_of_reddit_message = set()
DAY = 86400
days_ago = 30
current_time = time.strftime('%m-%d-%Y', time.localtime(time.time()))
current_time_minus_xdays = time.time() - days_ago * DAY
x_days_ago = time.strftime('%m-%d-%Y', time.localtime(current_time_minus_xdays))
post_per_query = {}
comments_per_query = {}
worksheets = []
workbook_name = f"30dReport_{x_days_ago}_{current_time}.xlsx"
workbook = xlsxwriter.Workbook(workbook_name)
format = workbook.add_format()
format.set_align('left')
channel_id = "C03PMAFFK50"
number_of_slack_message_to_retrieve = 2
number_of_messages_to_get_from_pushshift = 2
# if query has spaces, need to wrap it in \"query with spaces\"
# queries = ['addigy', 'mosyle', 'kandji', 'jamf', "\"manage apple devices\"", 'apple school manager',
#            'apple business manager', 'apple business chat']


# queries = ['asdfjjakksdkkall12223']
queries = ['\"addigy\"', 'apple']

# Store conversation history
def get_reddit_time_stamp_from_messages_in_slack():
    # conversation_history = []
    # ID of the channel you want to send the message to
    # channel_id = "C03PMAFFK50"

    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id, limit=number_of_slack_message_to_retrieve)

        conversation_history = result["messages"]
        # If a message is not made by the bot, skip it since only bot message will have the reddit post timestamp
        for message in conversation_history:
            # only thing I found unique to distinguish messages
            # if message["blocks"][0]["type"] == 'section':
            time_stamp_of_reddit_message.add(message['text'])
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


slack_channel = '#general'


def get_posts_from_pushshift(url):
    r = ''
    number_of_tries = 0
    while True:
        try:
            # Pushshift API rate limit is 60 requests per minute(1 request per second)
            if number_of_tries <= 4:
                # Adding sleep to avoid hitting the limit
                time.sleep(1)
                r = requests.get(url)
                if r.status_code != 200:
                    number_of_tries += 1
                    print("error code", r.status_code)
                    time.sleep(7)
                    continue
                else:
                    break
            else:
                return []
        except Exception as e:
            print("error: ", e)
            time.sleep(5)
            continue
    return json.loads(r.text, strict=False)


def create_xlsx_report(queries):
    for query in queries:
        worksheets.append(workbook.add_worksheet(query.replace('\"', '').capitalize()))

        url_to_get_posts = f"https://api.pushshift.io/reddit/submission/search/?q={query}&after=" \
                           f"{int(current_time_minus_xdays)}&size=500"
        post_in_last_x_days = get_posts_from_pushshift(url_to_get_posts)

        url_to_get_comments = f"https://api.pushshift.io/reddit/comment/search/?q={query}&after=" \
                              f"{int(current_time_minus_xdays)}&size=500"
        comments_in_last_x_days = get_posts_from_pushshift(url_to_get_comments)

        if post_in_last_x_days or comments_in_last_x_days:
            iterating_through_posts_for_report(post_in_last_x_days, query)

            iterating_through_comments_for_report(comments_in_last_x_days, query)

        else:
            print("There's been an error with the API")
            continue
    if post_in_last_x_days or comments_in_last_x_days:
        col = 0
        data = [
            ['Keyword', 'Sub-reddit', 'Occurrences as Posts', 'Occurrences as Comments']
        ]
        i = 0
        # print the worksheets
        for worksheet in worksheets:
            row = 0
            worksheet.write(row, col, data[0][0])
            worksheet.write(row, col + 1, data[0][1])
            worksheet.write(row, col + 2, data[0][2])
            worksheet.write(row, col + 3, data[0][3])
            row += 2
            for sub_reddit in post_per_query[queries[i]]:
                worksheet.write(2, col, queries[i].replace('\"', '').capitalize())
                worksheet.write(row, col + 1, sub_reddit, format)
                worksheet.write(row, col + 2, post_per_query[queries[i]][sub_reddit], format)
                row += 1
            for sub_reddit in comments_per_query[queries[i]]:
                worksheet.write(2, col, queries[i].replace('\"', '').capitalize())
                worksheet.write(row, col + 1, sub_reddit)
                worksheet.write(row, col + 3, comments_per_query[queries[i]][sub_reddit], format)
                row += 1

            worksheet.write(row + 1, 0, 'Total Mentions of Keyword:')
            worksheet.write(row + 1, 1, '=SUM(C3:C' + str(row) + ')+SUM(D3:D' + str(row) + ')', format)
            worksheet.set_column("A:D", 25)
            i += 1
        workbook.close()

        uploading_report_to_slack()


def uploading_report_to_slack():
    try:
        # Call the files.upload method using the WebClient
        # Uploading files requires the `files:write` scope
        result = client.files_upload(
            channels=channel_id,
            initial_comment="30 day report :smile:",
            file=workbook_name,
            text=time.time()
        )
        # Log the result
        logger.info(result)

    except SlackApiError as e:
        logger.error("Error uploading file: {}".format(e))


def iterating_through_comments_for_report(comments_in_last_x_days, query):
    comments_for_keyword_subreddit = {}
    for _ in comments_in_last_x_days['data']:
        if "r/" + _['subreddit'] not in comments_for_keyword_subreddit:
            comments_for_keyword_subreddit["r/" + _['subreddit']] = 1
        else:
            comments_for_keyword_subreddit["r/" + _['subreddit']] += 1
    comments_per_query[query] = comments_for_keyword_subreddit


def iterating_through_posts_for_report(post_in_last_x_days, query):
    posts_for_keyword_subreddit = {}
    for _ in post_in_last_x_days['data']:
        if "r/" + _['subreddit'] not in posts_for_keyword_subreddit:
            posts_for_keyword_subreddit["r/" + _['subreddit']] = 1
        else:
            posts_for_keyword_subreddit["r/" + _['subreddit']] += 1
    post_per_query[query] = posts_for_keyword_subreddit


def new_post_to_slack(query):
    get_reddit_time_stamp_from_messages_in_slack()

    url_to_get_posts = f"https://api.pushshift.io/reddit/submission/search/?q={query}&size=" \
                       f"{number_of_messages_to_get_from_pushshift} "
    posts = get_posts_from_pushshift(url_to_get_posts)

    if posts:
        # Reversing the data returned so the newest message will post last
        i = len(posts['data']) - 1
        for _ in reversed(posts['data']):
            if str(posts['data'][i]['created_utc']) not in time_stamp_of_reddit_message:
                post_created_date = time.strftime('%b %d %Y %I:%M%p',
                                                  time.localtime(posts['data'][i]['created_utc']))
                post_title = posts['data'][i]['title']
                url_of_post = posts['data'][i]['full_link']
                user_name = posts['data'][i]['author']
                if posts['data'][i]['subreddit_id'] is not None:
                    sub_reddit = f"r/{posts['data'][i]['subreddit']}"
                else:
                    sub_reddit = 'no info available'

                url_to_get_user_statistics = f"https://api.pushshift.io/reddit/submission/search/?author={user_name}&q=" \
                                             f"{query}&after={int(current_time_minus_xdays)}"

                user_data = get_posts_from_pushshift(url_to_get_user_statistics)

                user_sentiment = get_user_sentiment(posts, i, post_title, 'post')

                frequency_of_posts_str = get_frequency_of_posts(query, user_data, user_name, 'post')

                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":reddit: New Post Mentioning the Keyword: " + query.replace('\"', '').capitalize(),
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{url_of_post}|{post_title}>*"
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
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Sentiment Analysis of Post:*\n{user_sentiment}"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]
                # sending reddit post time stamp to slack, so we can later check if the post has already been posted
                send_to_slack(blocks, posts, i)
            else:
                print('no new posts')
            i -= 1
    else:
        print("Ther's been an error with the API")


def new_comment_to_slack(query):
    get_reddit_time_stamp_from_messages_in_slack()

    url_to_get_comment = f"https://api.pushshift.io/reddit/comment/search/?q={query}&size=" \
                         f"{number_of_messages_to_get_from_pushshift} "
    comments = get_posts_from_pushshift(url_to_get_comment)

    if comments:
        i = len(comments['data']) - 1
        for _ in reversed(comments['data']):
            if str(comments['data'][i]['created_utc']) not in time_stamp_of_reddit_message:
                comment_created_date = time.strftime('%b %d %Y %I:%M%p',
                                                     time.localtime(comments['data'][i]['created_utc']))
                full_comment = comments['data'][i]['body']
                url_of_comment = f"https://www.reddit.com{comments['data'][i]['permalink']}"
                user_name = f"{comments['data'][i]['author']}"
                sub_reddit = f"r/{comments['data'][i]['subreddit']}"

                url_to_get_user_statistics = f'https://api.pushshift.io/reddit/comment/search/?author={user_name}&q=' \
                                             f'{query}&after={int(current_time_minus_xdays)}'
                user_data = get_posts_from_pushshift(url_to_get_user_statistics)

                user_sentiment = get_user_sentiment(comments, i, full_comment, 'comment')

                frequency_of_comments_str = get_frequency_of_posts(query, user_data, user_name, 'comment')

                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":reddit: New Comment Mentioning the Keyword: " + query.replace('\"', '').capitalize(),
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{url_of_comment}|View Comment>*"
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
                                "text": "*Type:*\nComment\n"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*When:*\n{comment_created_date}\n"
                            },
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Frequency of comments:*\nIn the last 30 days, {frequency_of_comments_str}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Sentiment Analysis of comment:*\n{user_sentiment}"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]
                send_to_slack(blocks, comments, i)
            else:
                print('no new comments')
            i -= 1
    else:
        print("There's been an error with the API")


def send_to_slack(blocks, posts, i):
    post_date_creation = posts['data'][i]['created_utc']
    requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_bot_reddit,
        'channel': slack_channel,
        'text': post_date_creation,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


def get_frequency_of_posts(query, user_data, user_name, comment_or_post):
    frequency_of_posts_or_comment = len(user_data['data'])
    if comment_or_post == 'post':
        if frequency_of_posts_or_comment > 1:
            frequency_of_posts_str = f"u/{user_name} has made {frequency_of_posts_or_comment} posts mentioning the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "*"
        elif frequency_of_posts_or_comment == 0:
            frequency_of_posts_str = f"u/{user_name} has made no posts mentioning" + " the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "* (this is older than 1 month)"
        else:
            frequency_of_posts_str = f"u/{user_name} has made {frequency_of_posts_or_comment} post mentioning the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "*"
        return frequency_of_posts_str
    elif comment_or_post == 'comment':
        if frequency_of_posts_or_comment > 1:
            frequency_of_comment_str = f"u/{user_name} has made {frequency_of_posts_or_comment} comments mentioning the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "*"
        elif frequency_of_posts_or_comment == 0:
            frequency_of_comment_str = f"u/{user_name} has made no comments mentioning" + " the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "* (this is older than 1 month)"
        else:
            frequency_of_comment_str = f"u/{user_name} has made {frequency_of_posts_or_comment} comment mentioning the Keyword: *" + \
                                     query.replace('\"', '').capitalize() + "*"
        return frequency_of_comment_str


def get_user_sentiment(posts, i, comment_or_post_body, comment_or_post):
    specific_model = pipeline(model="cardiffnlp/twitter-roberta-base-sentiment")
    if comment_or_post == 'post':
        body_of_post = posts['data'][i]['selftext']
        if len(body_of_post) > len(comment_or_post_body):
            sentiment = specific_model(body_of_post[0:1200])
        else:
            sentiment = specific_model(comment_or_post_body[0:1200])
    else:
        sentiment = specific_model(comment_or_post_body[0:1200])

    if sentiment[0]['label'] == 'LABEL_0':
        user_sentiment = f"{round(sentiment[0]['score'] * 100)}% Negative"
    elif sentiment[0]['label'] == 'LABEL_1':
        user_sentiment = f"{round(sentiment[0]['score'] * 100)}% Neutral"
    elif sentiment[0]['label'] == 'LABEL_2':
        user_sentiment = f"{round(sentiment[0]['score'] * 100)}% Positive"
    else:
        user_sentiment = "No sentiment available"
    return user_sentiment


user_input = -1

while user_input != '5':
    # if query has spaces, need to wrap it in \"query with spaces\"
    # queries = ['addigy', 'mosyle', 'kandji', 'jamf', "\"manage apple devices\"", 'apple school manager',
    #            'apple business manager', 'apple business chat']
    # # queries = ['asdfjjakksdkkall12223']
    # # queries = ['\"addigy\"']
    print("\n\nEnter 1 to check for new posts")
    print("Enter 2 to check for new comments")
    print("Enter 3 for 30day report\n")
    user_input = input('enter choice: ')
    if user_input == '1':
        # iterating through the queries
        for query in queries:
            new_post_to_slack(query)
    elif user_input == '2':
        for query in queries:
            new_comment_to_slack(query)
    elif user_input == '3':
        create_xlsx_report(queries)
    else:
        print('no new posts')

    get_reddit_time_stamp_from_messages_in_slack()
