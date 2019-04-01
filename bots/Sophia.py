import os
import time
import re
import random
import datetime
from Memia import Memia

# Config file with Slack API Key
from config import config

from tinydb import TinyDB, Query
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(config.SOPHIA_BOT_TOKEN)

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "/info"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# Get the channels list and identifiers:
channels = slack_client.api_call("conversations.list")['channels']
users    = slack_client.api_call("users.list")

# db = TinyDB('./db/db.json')
# db.insert({'int': 1, 'char': 'a'})

memia = None

# Auxiliar methods to translate channel names
# to IDs and IDs to names.
def get_channel_name_by_id(channel_id):
    for channel in channels:
        if channel['id'] == channel_id:
            return channel['name']
    raise ValueError('Channel ID not found!')

def get_channel_id_by_name(channel_name):
    for channel in channels:
        if channel['name'] == channel_name:
            return channel['id']
    raise ValueError('Channel name not found!')

# def give_points(sender, receiver, n_points):
#     return 0


# To-do: decouple messages.
def get_info_for_channel(channel):

    info = ''

    if channel == 'lectura-de-papers':
        info += '''*- Papers leídos anteriormente en el canal -*
-----------------------------------------------------
:page_facing_up: - Paper 01 - *Neural Ordinary Differential Equations* : https://arxiv.org/abs/1806.07366
:page_facing_up: - Paper 02 - *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding* : https://arxiv.org/abs/1810.04805
:page_facing_up: - Paper 03 - *Attention Is All You Need* : https://arxiv.org/abs/1706.03762

*- Y esta semana... -*
-----------------------------------------------------
:memo: - Paper 04 - *Distilling the Knowledge in a Neural Network* - Cómo hacer modelos más eficientes y pequeños que aprenden de otros modelos más grandes : https://arxiv.org/abs/1503.02531
 
'''.format('')

        init_date = 2 # Wednesday
        today = datetime.date.weekday(datetime.date.today())

        if (init_date - today) % 7 + 1 == 1:
            info += ''':alarm_clock: *Hoy es el último día* para leer y discutir este artículo. ¡Anímate! :alarm_clock:'''
        if (init_date - today) % 7 + 1 > 1:
            info += ''':alarm_clock: Quedan *{} días* para leer y discutir este artículo. ¡Anímate! :alarm_clock:'''.format((init_date - today) % 7 + 1)

    else:
        info += "No hay ninguna información registrada para el canal #" + channel + ". Próximamente los moderadores se encargarán de resolver esto."

    return info

# slack_client.api_call(
#   "chat.postMessage",
#   channel=get_channel_id_by_name('women-in-ml'),
#   text="Les dejo este tweet por aquí :sophia: : https://twitter.com/BecomingDataSci/status/1094659297949241351"
# )
#
# slack_client.api_call(
#   "chat.postMessage",
#   channel=get_channel_id_by_name('1_chat-general'),
#   text="@AntonIA !!! ¿¿Dónde estás?? Que te reviento, QUE TE REVIENTO!! :glitch_crab:"
# )

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_responses = ["No te he entendido... Prueba a usar el comando *{}* para obtener información del canal.",
                         "¿Acaso te has leído mi manual de instrucciones? Usa el comando *{}* y te daré info del canal.",
                         "Error 404, comando no encontrado. Mejor usa el comando *{}* y te daré info del canal.",
                         "¿No querrás mejor utilizar el comando *{}* para obtener más información del canal?"]

    default_response = random.choice(default_responses)

    default_response = default_response.format(EXAMPLE_COMMAND)
    # default_response = "Wall-E?".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = get_info_for_channel(get_channel_name_by_id(channel))
    if command.find("meme") is not -1:
        memia.cmd(slack_client, command, channel)
        return

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        memia = Memia()
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print("Received command :" + command)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")