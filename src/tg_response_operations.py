import pandas as pd
import re

def get_msg_chat_id(msg):
    return msg["chat"]["id"]

def get_msg_address(msg):
    address = f'https://t.me/c/{str(msg["chat"]["id"])[4:]}/{msg["reply_to_message_id"]}/{msg["id"]}'
    return address

def validate_message_type(msg):
    if msg.get('_') == 'Message' and "reply_to_message_id" in msg:
        return True
    return False

def get_message_date(msg):
    return msg.get("date", "")

def get_message_text(msg):
    full_text = f'{msg.get("text", "")}\n{msg.get("caption", "")}'
    return full_text

def get_chat_topic(msg):
    msg['topic_id'] = msg['reply_to_message_id'] if 'reply_to_top_message_id' not in msg else msg['reply_to_top_message_id']
    
    topics_file_path = 'chats_topics.csv'
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
