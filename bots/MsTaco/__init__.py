import re
import time

import src.slack as slack
import src.use_cases as use_cases
from src.config import RESET_HOUR, MENTION_REGEX, RTM_READ_DELAY, TACO, HALF_TACO
from src.time_utils import update_time


# event handlers
def handle_daily_bonus(event):
    if 'user' in event:
        use_cases.give_bonus_taco_if_required(event['user'])


def handle_mention(event):
    if TACO in event["text"] or HALF_TACO in event["text"]:
        matches = re.search(MENTION_REGEX, event["text"])
        giver_id = event["user"]
        receiver_id = matches.group(1) if matches else None
        given_tacos = event["text"].count(TACO) + event["text"].count(HALF_TACO) * 0.5
        channel = event["channel"]

        if giver_id != slack.starterbot_id and receiver_id != slack.starterbot_id and giver_id != receiver_id:
            use_cases.give_tacos(giver_id, receiver_id, given_tacos, False, channel)


def handle_reaction(event):
    if (TACO.replace(':', '') == event["reaction"] or HALF_TACO.replace(':', '') == event["reaction"]) and 'item_user' in event:
        giver_id = event["user"]
        receiver_id = event['item_user']
        given_tacos = 1 if event['reaction'] == TACO.replace(':', '') else 0.5
        channel = event["item"]["channel"]

        if giver_id != slack.starterbot_id and receiver_id != slack.starterbot_id and giver_id != receiver_id:
            use_cases.give_tacos(giver_id, receiver_id, given_tacos, True, channel)


def handle_direct_command(event):
    command = use_cases.extract_direct_command(event["text"])

    if command == '/leaderboard':
        use_cases.print_leaderboard(event["channel"])

    if command == '/leaderboard_me':
        use_cases.print_leaderboard_me(event["channel"], event["user"])

    if command == '/weeklyleaderboard':
        use_cases.print_weekly_leaderboard(event["channel"])


# main loop
if __name__ == "__main__":
    while True:
        #use_cases.reset_daily_tacos()
        if slack.setup():
            print("Starter Bot connected and running!")
            while True:
                is_new_day = update_time()
                if is_new_day:
                    use_cases.reset_daily_tacos()

                events = slack.get_events()
                if events is False: break;

                for event in events:
                    if event["type"] == "message" and not "subtype" in event:
                        handle_daily_bonus(event)
                        handle_mention(event)
                    elif event["type"] == "reaction_added":
                        handle_reaction(event)
                
                    if event["type"] == "message" and not "subtype" in event:
                        handle_direct_command(event)

                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")
