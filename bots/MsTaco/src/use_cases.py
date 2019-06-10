import re
import operator
import src.persistence as persistence
import src.slack as slack
from src.config import DAILY_TACOS, MENTION_REGEX
from src.time_utils import get_today, get_time_left


def give_tacos(giver_id, receiver_id, given_tacos, reaction=False, channel=None):
    giver = persistence.DBUser(giver_id)
    receiver = persistence.DBUser(receiver_id)

    if giver.remaining_tacos() >= given_tacos:
        receiver.add_tacos(given_tacos)
        giver.remove_tacos(given_tacos)

        _notify_tacos_sent(giver.user_id, receiver.user_id, given_tacos, giver.remaining_tacos())
        _notify_tacos_received(giver.user_id, receiver.user_id, given_tacos, receiver.owned_tacos(), channel)

        _log_taco_transaction(giver.user_id, receiver.user_id, given_tacos, reaction, get_today())
    else:
        _notify_not_enough_tacos(giver.user_id, get_time_left())


def give_bonus_taco_if_required(user_id):
    user = persistence.DBUser(user_id)

    if user.requires_bonus_taco():
        user.add_tacos(1, bonus=True)

        _notify_bonus_taco(user.user_id, user.owned_tacos())
        _log_bonus_taco(user.user_id, get_today())


def reset_daily_tacos():
    persistence.DBUser.reset_daily_tacos()

    # Compute all the tacos from yesterday.
    daily_taco_count = persistence.daily_taco_cunt()

    message = f"*¡INFO-TACO!* El número total de tacos repartidos ayer en la comunidad es de *{daily_taco_count}x :taco: *"
    slack.send_message(slack.channel_to_id['1_chat-general'], message)
    print_leaderboard(slack.channel_to_id['1_chat-general'])


def print_leaderboard(channel):
    message = '*MLH Taco Leaderboard :taco:*\n'
    db_list = persistence.DBUser.get_top_ranking()
    bots_id = [None, 'UGMETH49H']

    i = 1
    top_n = 10

    # Top 10 elements
    for l in db_list:
        if i <= min(len(db_list), top_n):
            if l['user_id'] not in bots_id:
                message += str(i) + "). " + "<@" + l['user_id'] + "> `" + str(l['owned_tacos']) + "`\n"
                i += 1
        else:
            break

    slack.send_message(channel, message)

def print_weekly_leaderboard(channel):
    message = '*MLH Taco Weekly Leaderboard :taco:*\n'
    db_list = persistence.DBUser.get_weekly_info()
    bots_id = [None, 'UGMETH49H']

    i = 1
    top_n = 10

    week_logs = {}

    # Reduce weekly logs to get the total number of tacos per user.
    for log in db_list:
        user = log['receiver_user']
        if user != None:
            if user in week_logs:
                week_logs[user] = week_logs[user] + log['n_tacos']
            else:
                week_logs.update({user: log['n_tacos']})

    week_logs = sorted(week_logs.items(), key=operator.itemgetter(1), reverse=True)

    # Top 10 elements
    for user_id, n_tacos in week_logs:
        if i <= min(len(db_list), top_n):
            if user_id not in bots_id:
                message += str(i) + "). " + "<@" + user_id + "> `" + str(n_tacos) + "`\n"
                i += 1
        else:
            break

    slack.send_message(channel, message)



def extract_direct_command(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    if matches is None: return
    user_id = matches.group(1)
    if matches and user_id == slack.starterbot_id:
        return matches.group(2).strip()
    else:
        return None


def _log_taco_transaction(giver_id, reciver_id, amount, reaction, date):
    persistence.save_log({
        'giving_user': giver_id,
        'receiver_user': reciver_id,
        'n_tacos': amount,
        'type': 'reaction' if reaction else 'message',
        'date': date
    })


def _log_bonus_taco(user_id, date):
    persistence.save_log({
        'giving_user': None,
        'receiver_user': user_id,
        'n_tacos': 1,
        'type': 'bonus',
        'date': date
    })


def _notify_tacos_sent(giver_id, reciver_id, amount, remaining):
    message = f"¡<@{reciver_id}> *ha recibido {amount} x :taco:* de tu parte! Te quedan {remaining} tacos para repartir hoy."
    slack.send_message(giver_id, message)


def _notify_tacos_received(giver_id, reciver_id, amount, total, channel):
    message = f"¡*Has recibido {amount} x :taco: * de <@{giver_id}> en el canal <#{channel}>! Ya tienes *{total}x :taco: "
    slack.send_message(reciver_id, message)


def _notify_not_enough_tacos(giver_id, time_before_reset):
    message = f"*¡No tienes suficientes tacos!* Recibirás {DAILY_TACOS} TACOS NUEVOS :taco: recién cocinados en *{time_before_reset} horas.*"
    slack.send_message(giver_id, message)


def _notify_bonus_taco(user_id, total):
    message = f"¡Toma! Aquí tienes *1 TACO de premio por participar hoy en la comunidad*. Ya tienes *{total}x :taco: * ¡Vuelve mañana a por más!"
    slack.send_message(user_id, message)
