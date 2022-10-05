import json
import requests

from slack_token import *

slack_token = slack_token_code
slack_channel = '#general'
slack_icon_emoji = ':see_no_evil:'
slack_user_name = 'Double Images Monitor'


# def post_message_to_slack(text, blocks):
def post_message_to_slack(text):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'icon_emoji': slack_icon_emoji,
        'username': slack_user_name,
        # 'blocks': json.dumps(blocks) if blocks else None
    }).json()


# Define Your Query
# query = "verrakoooo"
# query = "000000ortencialulusss"
query = "peroporqueque"
url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
# url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
r = requests.get(url)

# comments = set()

# print(comments)
# comments.add('hecore')
# print(comments)

data = json.loads(r.text, strict=False)
print(r.text)
print('\n\nfirstdata')
print(data)
# print('\n\narchived')
# print(data['data'][0]['archived'])

# if "hecoree" in comments:
#     print('yes it is')
# else:
#     print('no')

# loop through data object
# count = 0
# for item in data['data']:
#     print(data['data'][count]['permalink'])
#     count += 1
#     comments.add(item['body'])
#
# print('\n----------------------------\n')
# print(comments)

userInput = -1
comments = set()
while userInput != '5':
    print("\n\nenter 1 to check for new posts and comments")
    userInput = input('enter choice: ')
    if userInput == '1':
        count = 0
        query = "addigy"
        url = f"https://api.pushshift.io/reddit/search/comment/?q={query}"
        # url = f"https://api.pushshift.io/reddit/search/submission/?q={query}"
        r = requests.get(url)

        data = json.loads(r.text, strict=False)
        for item in data['data']:
            if data['data'][count]['permalink'] not in comments:
                print('not in set adding new comment')
                print(data['data'][count]['permalink'])
                comments.add(item['permalink'])
                print(count, "__", item['permalink'])
                slack_message = str(count) + "__" + item['permalink']
                # blocks = [{
                #     "type": "section",
                #     "text": {
                #         "type": "mrkdwn",
                #         "text": ":check: The script has run successfully on the dev."
                #     }
                # }]
                # post_message_to_slack(slack_message, blocks)
                post_message_to_slack(slack_message)
            else:
                print('no new posts')
            count += 1
        print(comments)
        # print(r.text)

# ID of the channel you want to send the message to
# channel_id = "general"
#
# try:
#     # Call the chat.postMessage method using the WebClient
#     result = client.chat_postMessage(
#         channel=channel_id,
#         text="Hello world"
#     )
#     logger.info(result)
#
# except SlackApiError as e:
#     logger.error(f"Error posting message: {e}")

# print(data['data'][0]['body'])
# urlInfo = data['data'][0]['permalink']
# print(urlInfo)
# postUrl = f"https://www.reddit.com{urlInfo}"
# print('printing url')
# print(postUrl)
# print(r.content)
# json_response = r.json()
# print(json.dumps(json_response, indent=2))
# print('\n-----------------------------\n')
# for key in json_response:
#     value = json_response[key]
#     for key2 in value:
#         print(key2)
#         print('down here')
#     print("The key and value are ({}) = ({})".format(key, value))
#
#     theValue = value[0]
#
# # print(theValue.archived)
# print('\n-----------------------------\n')
# hmmm = flatten(theValue)
# print(hmmm)
