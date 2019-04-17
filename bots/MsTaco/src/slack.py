from slackclient import SlackClient

from src.config import MSTACO_BOT_TOKEN

slack_client = SlackClient(MSTACO_BOT_TOKEN)

channels = slack_client.api_call("conversations.list")['channels']
users = slack_client.api_call("users.list")

starterbot_id = None

# Auxiliar dictionaries to translate channel names
# to IDs and IDs to names.
id_to_channel = {channel['id']: channel['name'] for channel in channels}
channel_to_id = {channel['name']: channel['id'] for channel in channels}


def send_message(user_id, message):
    slack_client.api_call(
        "chat.postMessage",
        channel=user_id,
        as_user=True,
        text=message
    )


def setup():
    global starterbot_id
    if slack_client.rtm_connect(with_team_state=False):
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        return True
    else:
        return False


def get_events():
    return slack_client.rtm_read()
