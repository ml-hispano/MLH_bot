import os
import json

import pandas as pd

#Unico parametro a configurar. PATH hacia la carpeta de descarga proporcionada por @Santi Iglesias
#https://drive.google.com/open?id=1RQz2jxV9T3Sv_B5D7wSB8Zux6P0gIS8-

channels_folder_path = 'chat_stream'

channels = [d for d in os.listdir(channels_folder_path) if os.path.isdir(os.path.join(channels_folder_path, d))]

df = pd.DataFrame(columns=['channel', 'user', 'message'])

for channel_name in channels:

    channel_path = os.path.join(channels_folder_path, channel_name)
    json_files = os.listdir(channel_path)

    for file_name in json_files:
        file = open(os.path.join(channel_path, file_name))
        messages = json.load(file)
        file.close()

        for msg in messages:
            if 'subtype' not in msg:
                row = pd.Series([channel_name, msg.get('user'), msg.get('text')], index=df.columns)
                df = df.append(row,
                               ignore_index=True)


df.to_csv('mensajes_slack.csv', index=False)
