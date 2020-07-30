import re
import operator
import src.persistence as persistence
import src.slack as slack
from src.config import DAILY_TACOS, MENTION_REGEX, URL_REGEX
from src.time_utils import get_today, get_time_left

def give_tacos(giver_id, receiver_id, given_tacos, reaction=False, channel=None, message=""):
    giver = persistence.DBUser(giver_id)
    receiver = persistence.DBUser(receiver_id)

    match_url = re.search(URL_REGEX, message)
    url = match_url.group(2) if match_url else None

    if giver.remaining_tacos() >= given_tacos:
        receiver.add_tacos(given_tacos, url=url)
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

    print_weekly_leaderboard(slack.channel_to_id['1_chat-general'])


def print_leaderboard(channel):

    # Compute all the tacos from yesterday.
    daily_taco_count = persistence.daily_taco_cunt()

    message = f"*¡INFO-TACO!* El número total de tacos repartidos ayer en la comunidad es de *{daily_taco_count}x :taco: \n\n*"

    message += '*MLH Leaderboard de Tacos :taco:*\n'
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

    # Compute all the tacos from yesterday.
    daily_taco_count = persistence.daily_taco_cunt()

    message = f"*¡INFO-TACO!* El número total de tacos repartidos ayer en la comunidad es de *{daily_taco_count}x :taco: *\n"

    db_list = persistence.DBUser.get_weekly_info()
    bots_id = [None, 'UGMETH49H']

    is_final = False # Is the final leaderboard?

    if len(db_list) == 0:
        message += '*MLH Leaderboard Semanal Final de Tacos :taco:*\n'
        db_list  = persistence.DBUser.get_prev_weekly_info()
        is_final = True

    else:
        message += '*MLH Leaderboard Semanal de Tacos :taco:*\n'

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
                if (is_final and i < 4):
                    medals = [":first_place_medal:", ":second_place_medal:", ":third_place_medal:"]
                    message +=  medals[i-1] + " " + "<@" + user_id + "> `" + str(n_tacos).replace('.0','') + "`\n"
                else:
                    message +=     str(i) + "). " + "<@" + user_id + "> `" + str(n_tacos).replace('.0', '') + "`\n"

                i += 1
        else:
            break

    if is_final:
        message += "\n *¡El ranking semanal de tacos ha sido reiniciado!*"

    slack.send_message(channel, message)


def print_leaderboard_me(channel, user):

    db_list = persistence.DBUser.get_top_ranking()

    # Find user in ranking
    users_generator = ({'pos':i + 1, 'info':db_info} for i, db_info in enumerate(db_list) if db_info['user_id'] == user)

    user_taco = next(users_generator)

    # If not in ranking, maybe it's a error or the user doesn't have tacos
    if user_taco is None:
        message = '*No apareces en nuestro registro de tacos :sad_parrot:. ¿Has recibido algún taco?*\n'

    else:
        message = ":taco: Stats de <@" + user + ">:\n"
        message += "\t\t*Posición: * `" +  str(user_taco['pos']) + "` \n"
        message += "\t\t*Tacos:    * `" +  str(user_taco['info']['owned_tacos']) + "`  \n"

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
