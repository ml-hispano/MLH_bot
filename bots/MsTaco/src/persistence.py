import os
from tinydb import TinyDB, Query
from tinydb.operations import add, subtract

from src.config import DAILY_TACOS
from src.time_utils import get_today

users_db = TinyDB('./db/users.json')
logs_db = TinyDB('./db/logs.json')


class DBUser:
    def __init__(self, user_id):
        self.user = self.get_user(user_id)
        self.user_id = self.user['user_id']

    @staticmethod
    def get_user(user_id):
        db_user = users_db.get(Query()['user_id'] == user_id)

        # If giving user not in DB. Create it!
        if not db_user:
            db_user_id = users_db.insert({
                'user_id': user_id,
                'daily_tacos': DAILY_TACOS,
                'daily_bonus': True,
                'owned_tacos': 0
            })
            db_user = users_db.get(doc_id=db_user_id)

        return db_user

    @staticmethod
    def reset_daily_tacos():
        users_db.update({'daily_tacos': DAILY_TACOS, 'daily_bonus': True})

    @staticmethod
    def get_top_ranking():
        return sorted(users_db.all(), key=lambda k: k['owned_tacos'], reverse=True)

    def update(self):
        self.user = users_db.get(Query()['user_id'] == self.user_id)

    def add_tacos(self, amount, bonus=False):
        users_db.update(add('owned_tacos', amount), Query()['user_id'] == self.user_id)
        if bonus:
            users_db.update({'daily_bonus': False}, Query()['user_id'] == self.user_id)
        self.update()

    def remove_tacos(self, amount):
        users_db.update(subtract('daily_tacos', amount), Query()['user_id'] == self.user_id)
        self.update()

    def remaining_tacos(self):
        return self.user['daily_tacos']

    def owned_tacos(self):
        return self.user['owned_tacos']

    def requires_bonus_taco(self):
        return self.user['daily_bonus'] == True


def save_log(log):
    logs_db.insert(log)


def daily_taco_cunt():
    return sum([i['n_tacos'] for i in logs_db.search((Query().date == get_yesterday()))])
