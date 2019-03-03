import os
import time
import re
import random
import datetime

# Config file with Slack API Key
from config import config

from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(config.MSTACO_BOT_TOKEN)

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "/info"
MENTION_REGEX = "<@(|[WU].+?)>(.*)"

# Get the channels list and identifiers:
channels = slack_client.api_call("conversations.list")['channels']
users = slack_client.api_call("users.list")

# Auxiliar methods to translate channel names
# to IDs and IDs to names.
def get_channel_name_by_id(channel_id):
    for channel in channels:
        if channel['id'] == channel_id:
            return channel['name']
    return ""
    # raise ValueError('Channel ID not found!')


def get_channel_id_by_name(channel_name):
    for channel in channels:
        if channel['name'] == channel_name:
            return channel['id']
    return ""
    # raise ValueError('Channel name not found!')


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

        init_date = 2  # Wednesday
        today = datetime.date.weekday(datetime.date.today())

        if (init_date - today) % 7 + 1 == 1:
            info += ''':alarm_clock: *Hoy es el último día* para leer y discutir este artículo. ¡Anímate! :alarm_clock:'''
        if (init_date - today) % 7 + 1 > 1:
            info += ''':alarm_clock: Quedan *{} días* para leer y discutir este artículo. ¡Anímate! :alarm_clock:'''.format(
                (init_date - today) % 7 + 1)

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

from tinydb import TinyDB, Query
from tinydb.operations import add, subtract

db = TinyDB('./db/users.json')

# Should be located into a table.
db_logs = TinyDB('./db/logs.json')

DAILY_TACOS = 5

def give_tacos(giving_user, receiv_user, n_tacos, reaction=False):

 user = Query()

 init_user(giving_user)
 init_user(receiv_user)

 giving_owned_tacos = db.search(user.user_id == giving_user)[0]['daily_tacos']

 if giving_owned_tacos - n_tacos >= 0:
     db.update(add('owned_tacos', n_tacos),      user.user_id == receiv_user)
     db.update(subtract('daily_tacos', n_tacos), user.user_id == giving_user)

     # LOG to DB
     db_logs.insert({'giving_user' : giving_user, 'receiver_user' : receiv_user, 'n_tacos' : n_tacos, 'type' : 'reaction' if reaction else 'message', 'date' : today })

     slack_client.api_call(
         "chat.postMessage",
         channel=giving_user,
         as_user=True,
         text="¡<@" + receiv_user + "> *ha recibido {0:g} x :taco:* de tu parte!".format(n_tacos))

     slack_client.api_call(
         "chat.postMessage",
         channel=receiv_user,
         as_user=True,
         text=("¡ *Has recibido {0:g} x :taco: * de <@" + giving_user + ">!").format(n_tacos))

 else:

     slack_client.api_call(
         "chat.postMessage",
         channel=giving_user,
         as_user=True,
         text="*¡No tienes suficientes tacos!* Recibirás {0:g} TACOS NUEVOS :taco: recién cocinados en *{1:} horas.*".format(DAILY_TACOS, time_left))

     # To-do: Send giving user private message : No more tacos! You have to wait... {Time}

 return None

def give_bonus_taco(user):

    # Give daily 'talking once' bonus taco.
    db.update(add('owned_tacos', 1),  Query().user_id == user)
    db.update({'daily_bonus': False}, Query().user_id == user)
    owned_tacos = db.search(Query().user_id == user)[0]['owned_tacos']

    db_logs.insert({'giving_user': None, 'receiver_user': user, 'n_tacos': 1, 'type': 'bonus', 'date' : today })

    slack_client.api_call(
        "chat.postMessage",
        channel=user,
        as_user=True,
        text="¡Toma! Aquí tienes *1 TACO de premio por participar hoy en la comunidad*. Ya tienes *{0:g}x :taco: * ¡Vuelve mañana a por más!".format(owned_tacos))

    return

def reset_daily_tacos():
    # Give new tacos and reset the 'talking once' bonus.
    db.update({'daily_tacos': DAILY_TACOS, 'daily_bonus' : True})

    # Compute all the tacos from yesterday.
    n_tacos = sum([i['n_tacos'] for i in db_logs.search((Query().date == today))])

    slack_client.api_call(
        "chat.postMessage",
        channel=get_channel_id_by_name('1_chat-general'),
        as_user=True,
        text="*¡INFO-TACO!* El número total de tacos repartidos ayer en la comunidad es de *{0:g}x :taco: *".format(n_tacos))

    print_leaderboard(get_channel_id_by_name('1_chat-general'))
    print("LOG: ¡Reset diario ejecutado!")

    return

def parse_taco_event(event, reaction=False):

    if not reaction:
        matches = re.search(MENTION_REGEX, event["text"])
        receiv_usr = matches.group(1) if matches else None
        n_tacos = event["text"].count(":taco:") + event["text"].count(":medio_taco:") / 2
    else:
        if 'item_user' in event:
            receiv_usr = event['item_user']
            n_tacos = 1 if event['reaction'] == "taco" else 0.5
        else:
            return None, None

    giving_usr = event["user"]

    # If user is not the bot, and giver and receiver are not the same...
    if (giving_usr != starterbot_id and receiv_usr and giving_usr != receiv_usr):
        give_tacos(giving_usr, receiv_usr, n_tacos, reaction)

    return None, None

def print_leaderboard(channel):

    mess = '*Machine Learning Hispano Leaderboard :taco:*\n'

    db_list = sorted(db.all(), key=lambda k: k['owned_tacos'], reverse=True)

    # Top 10 elements
    for i, l in enumerate(db_list[:min(len(db_list), 9)]):
        mess += str(i+1) + "). " + "<@" + l['user_id'] + "> `" + str(l['owned_tacos']) + "`\n"

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=True,
        text=mess)

    print(channel)
    print(mess)

    return


def init_user(user_id):

    db_user = db.search(Query()['user_id'] == user_id)

    # If giving user not in DB. Create it!
    if not db_user:
        db.insert({'user_id': user_id, 'daily_tacos': DAILY_TACOS, 'daily_bonus': True, 'owned_tacos': 0})


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:

        print(event)

        if event["type"] == "message" and 'user' in event:

            init_user(event['user'])

            if db.search(Query()['user_id'] == event['user'])[0]['daily_bonus'] == True:
                give_bonus_taco(event['user'])

        # Event : Detect taco emojis in message.
        if event["type"] == "message" and not "subtype" in event:
            if ":taco:" in event["text"] or ":medio_taco:" in event["text"]:
                return parse_taco_event(event, reaction=False)

        # Event : Detect taco reaction to message.
        if event["type"] == "reaction_added":
            print(event["item"])
            if "taco" == event["reaction"] or "medio_taco" == event["reaction"]:
                return parse_taco_event(event, reaction=True)

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

    if command.startswith('/leaderboard'):
        response = print_leaderboard(channel)


# Save today's day.
today = str(time.gmtime().tm_year) + str(time.gmtime().tm_mon).zfill(2) + str(time.gmtime().tm_mday).zfill(2)
# Save number of hours before reset.
time_left = 0
# Reset system at 6am.
RESET_HOUR = 6

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:

            command, channel = parse_bot_commands(slack_client.rtm_read())

            # Compare if now is not today anymore.
            now = str(time.gmtime().tm_year) + str(time.gmtime().tm_mon).zfill(2) + str(time.gmtime().tm_mday).zfill(2)

            # In that case, trigger the daily taco reset.
            if now != today:
                reset_daily_tacos()
                today = now
            else:
                time_left = (RESET_HOUR - time.gmtime().tm_hour) % 24
                # print("Not reset yet! Just wait {} hour(s)".format(())

            if command:
                print("Received command :" + command)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")