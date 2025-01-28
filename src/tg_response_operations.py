import pandas as pd
import re
import json

def get_msg_chat_id(msg):
    return msg["chat"]["id"]

#https://t.me/MoreOz/84594
#https://t.me/c/1438763209/84594

#https://t.me/c/2370426098/4935/4953 - invalid
#https://t.me/c/2370426098/4952/4953 - valid
#https://t.me/delfin_volna/1/4935


def get_msg_address(msg):
#    try:
        if "reply_to_message_id" in msg or "reply_to_top_message_id" in msg:
            msg_topic_id = msg['reply_to_message_id'] if 'reply_to_top_message_id' not in msg else msg['reply_to_top_message_id']
            address = f'https://t.me/c/{str(msg["chat"]["id"])[4:]}/{msg_topic_id}/{msg["id"]}'
        else:
            address = f'https://t.me/c/{str(msg["chat"]["id"])[4:]}/{msg["id"]}'
#    except:
        #print(json.dumps(msg, indent = 4))
#        return None
        return address

def validate_message_type(msg):
    if msg.get('_') == 'Message':
        return True
    return False

def get_message_date(msg):
    return msg.get("date", "")

def get_message_text(msg):
    text = ""
    if msg.text is not None:
        text = msg.text
    if msg.caption is not None:
        text = text + msg.caption
    return text

def get_chat_topic(message):
    msg = json.loads(str(message))
    if "reply_to_message_id" in msg or "reply_to_top_message_id" in msg:
        msg['topic_id'] = msg['reply_to_message_id'] if 'reply_to_top_message_id' not in msg else msg['reply_to_top_message_id']
    else: 
        return "Не известно..."

    
    topics_file_path = '../chats_topics.csv'
    topics_df = pd.read_csv(topics_file_path)
    # Фильтрация по chat_id = -1002415079849
    topics_filtered = topics_df[topics_df['chat_id'] == get_msg_chat_id(msg)]
    topics_dict = topics_filtered.set_index("topic_id").to_dict()["topic_name"]
    return topics_dict.get(msg['topic_id'], "Не известно...")

def get_coordinate_list_from_text(text):
    #coordinate_pattern = r'\d{1,3}\.\d{4,7}, ?\d{1,3}\.\d{4,7}'
    #coordinates = re.findall(coordinate_pattern, text)
    latitude_pattern = r"4[2-7]\.\d{5,7}"
    longitude_pattern = r"3[5-9]\.\d{5,7}"

    all_lat = re.findall(latitude_pattern, text.replace(",", "."))
    all_lon = re.findall(longitude_pattern, text.replace(",", "."))
    if len(all_lat) and len(all_lon):
        coordinates = f"{all_lat[0]}, {all_lon[0]}"
        return [coordinates]
    return None
