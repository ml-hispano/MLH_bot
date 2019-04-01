import io
import requests
import random

class Memia:
    # Where are uploaded the ML Memes
    GITHUB_USER = 'xirzag'
    GITHUB_REPO = 'MLH_bot'
    GITHUB_PATH = 'bots/ML Memes'

    def __init__(self):
        self.reload_memes()

    memes_urls = []

    def get_memes_urls(self):
        r = requests.get('https://api.github.com/repos/{}/{}/contents/{}'
                         .format(self.GITHUB_USER, self.GITHUB_REPO, self.GITHUB_PATH))
        response = r.json()

        blob_url = "https://raw.githubusercontent.com/{}/{}/master/{}/"\
            .format(self.GITHUB_USER, self.GITHUB_REPO, self.GITHUB_PATH)

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

    def cmd(self, slack_client, command, channel):
        image_url = self.random_meme()
        attachments = [{"title": ' ', "image_url": image_url}]
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=random.sample(self.random_meme_msg, 1)[0],
            attachments=attachments
        )



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