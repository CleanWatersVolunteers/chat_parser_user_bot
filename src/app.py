import logging
import asyncio
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime
from pyrogram import Client
from operator import itemgetter
from datetime import datetime

from coordinate_storage import coordinate_storage
from tg_response_operations import (
    validate_message_type, get_msg_address, get_message_date, get_message_text,
    get_chat_topic, get_coordinate_list_from_text
)

target_group_id = -1002276105317 #Мониторинг координат

channel_ids = {
    -1002415079849: "Megachat",
    -1001758075891: "Анапа. Море. ЧС.",
    -1002446870294: "Разлив Нефти Крым",
    -1002492992460: "БЕРЕГ СОЧИ. ЧС. Помощь птицам. Сочинское географическое общество"
}    


#https://t.me/sochi_bereg/4/9414
# vs https://t.me/c/2492992460/9412/9414            

with open("../__token_for_telegram_user.txt", "r") as f:
    api_id = f.readline()[:-1]
    api_hash = f.readline()

coordinate_storage.storage_init()

async def main() -> None:
    while(True):
        forward_list = []
        print("[..] Chat look-up...")
        async with Client("me", api_id, api_hash) as app:      
            for channel_id in channel_ids.keys():
                print(f"[..] Reading {channel_ids[channel_id]}")
                async for message in app.get_chat_history(int(channel_id)):
                    message = str(message)
                    message_dict = json.loads(message)
                    #print(json.dumps(message_dict, indent = 4))
                    coordinates = get_coordinate_list_from_text(message)
                    print(".", end="")
                    if not validate_message_type(message_dict):
                        continue
                    appended = coordinate_storage.storage_append(message_dict)                    
                    if appended == False:
                        print("\n[OK] Found known coordinates. Breaking...")
                        break                    
                    if not coordinates: 
                        continue
                    print("\n")
                    forward_list.append(message_dict)
                    link = get_msg_address(message_dict)
                    date = get_message_date(message_dict)
                    message_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    start_time = "2025-01-05 01:25:00"
                    start_time_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    if message_datetime < start_time_datetime or len(forward_list) > 10:
                        print(f"Message: {message_datetime}. Time limit: {start_time_datetime}. Found: {len(forward_list)}")
                        break
                    print(f'[OK] Coordinates found. Appending: {date}, {link}')

            coordinate_storage.storage_flush()
            forward_list = sorted(forward_list, key=itemgetter('date'))
            print(f"[OK] Chat look-up finished {datetime.now()}")
            print(f"[OK] Forwarding {len(forward_list)} messages ...")   
            print(str('-'*25))         

            for msg in forward_list:
                link = get_msg_address(msg)
                date = get_message_date(msg)
                text = get_message_text(msg)
                topic = get_chat_topic(msg)
                send_text = f"{date}\n[{topic}]\n{link}\n{text}"
                coordinates = get_coordinate_list_from_text(json.dumps(msg))
                send_text = send_text + "\n" + coordinates[0] + "\n"
                await app.send_message(target_group_id, send_text)
                await asyncio.sleep(5)            
            await asyncio.sleep(1*15)

if __name__ == "__main__":
    asyncio.run(main())
