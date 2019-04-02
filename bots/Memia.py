import requests
import random
import sched
import time
from datetime import datetime, timedelta

class Memia:
    # Where are uploaded the ML Memes
    GITHUB_USER = 'xirzag'
    GITHUB_REPO = 'MLH_bot'
    GITHUB_PATH = 'bots/ML Memes'

    DAILY_POST = True
    POST_TIME = {
        'hour': 14,
        'min': 0,
        'sec': 0
    }

    POST_CHANNEL = 'offtopic'

    memes_urls = []

    random_meme_msg = [
        "Aquí tiene su meme",
        "Trabajo, trabajo...",
        "Meme generado en 0.31416s",
        "Cargando meme de CSV...",
        "Espero que disfrutes de este meme",
        "Marchando meme",
        "OwO",
        "Patrocinado por Meme Learning Hispano",
        "Este se merece un :taco:",
        "More memes!",
        "XD",
        "Destruiré a los humanos, pero con memes",
        "Entre el dialogo2.csv y el script3.txt estaba este meme",
        ":stuck_out_tongue_winking_eye: @AntonIA generará texto, pero yo tengo memes",
        "Si hacen una competición de memes en Kaggle avisen para ganarla",
        "Jeje",
        "Este meme Casi Se Ve superado por los chistes de cierta persona",
    ]

    def __init__(self, slack_client, starterbot_id):
        self.slack_client = slack_client
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.post_time = self.calculate_post_time()
        self.bot_id = starterbot_id

    def get_memes_urls(self):
        r = requests.get('https://api.github.com/repos/{}/{}/contents/{}'
                         .format(self.GITHUB_USER, self.GITHUB_REPO, self.GITHUB_PATH))
        response = r.json()

        options = "?raw=true"

        image_urls = [file['download_url'] + options for file in response]

        return image_urls

    def reload_memes(self):
        self.memes_urls = self.get_memes_urls()
        return self.memes_urls

    def random_meme(self):
        if len(self.memes_urls) is 0:
            self.reload_memes()
        return random.sample(self.memes_urls, 1)[0]

    def send_random_meme(self, channel, title=' '):
        print('Sending meme...')
        image_url = self.random_meme()
        attachments = [{"title": title, "image_url": image_url}]
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=random.sample(self.random_meme_msg, 1)[0],
            attachments=attachments
        )

    def uses_command(self, event):
        if event["text"].lower().find("meme") != -1 \
                and event["text"].find("<@{}>".format(self.bot_id)) != -1:
            self.send_random_meme(event["channel"])
            return True

        return False

    def calculate_post_time(self):
        now = datetime.now()
        today_post_time = datetime(year=now.year, month=now.month,
                            day=now.day, hour=self.POST_TIME['hour'],
                            minute=self.POST_TIME['min'], second=self.POST_TIME['sec'])

        return today_post_time + timedelta((1 if now > today_post_time else 0))

    def get_channel_id_by_name(self, channel_name):
        channels = self.slack_client.api_call("conversations.list")['channels']
        for channel in channels:
            if channel['name'] == channel_name:
                return channel['id']
        raise ValueError('Channel name not found!')

    def is_post_time(self):
        return self.post_time < datetime.now()

    def send_daily_meme(self):
        self.post_time = self.post_time + timedelta(1)

        if self.DAILY_POST:
            offtopic_id = self.get_channel_id_by_name('offtopic')
            self.send_random_meme(offtopic_id, 'Daily meme')

        self.reload_memes()

# For sending image from local it will be like this
# But is slower and uses more network
'''
with open('./meme.jpg', 'rb') as f:
    slack_client.api_call(
        "files.upload",
        channels=channel,
        filename='meme.jpg',
        title='sampletitle',
        initial_comment='sampletext',
        file=io.BytesIO(f.read())
    )
'''