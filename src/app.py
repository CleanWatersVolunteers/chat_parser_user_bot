import logging
import asyncio
import json
import re, copy
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

target_group_dolphins = -4731696810  # TODO verify ID

channel_ids = {
    -1002415079849: "Megachat",
    -1001758075891: "Анапа. Море. ЧС.",
    -1002446870294: "Разлив Нефти Крым",
    -1002492992460: "БЕРЕГ СОЧИ. ЧС. Помощь птицам. Сочинское географическое общество",
    -1002370426098: "ШТАБ \"Дельфины\" Спасаем море Побережье п.Волны - п.Таманский",
    -1002395237007: "Отлов птиц Новороссийск",
    -1001216424748: "Станица Благовещенская",
    -1001501303550: "Благовещенская🌊 MORE_BLAGA",
    -1002372014840: "Волонтеры! Усиление! Благовещенская!",
    -1002403069257: "Анапа. Волонтеры моря",
    -1002474270111: "Геленджик. Волонтёры Чёрного моря",
    -1002058018020: "Макс Анапский",
    -1001438763209: "Юрий Озаровский Анапа Витязево",
    -1001291670182: "ПВА Анапа"
}    


with open("../__token_for_telegram_user.txt", "r") as f:
    api_id = f.readline()[:-1]
    api_hash = f.readline()

coordinate_storage.storage_init()

async def main() -> None:
    while(True):
        forward_list = []
        forward_dolphin_list = []
        print("[..] Chat look-up...")
        async with Client("me", api_id, api_hash) as app:   
            async for dialog in app.get_dialogs(): pass

            for channel_id in channel_ids.keys():
                print(f"[..] Reading {channel_ids[channel_id]}")
                async for message in app.get_chat_history(int(channel_id)):
                    appended = coordinate_storage.storage_append(message)                    
                    if appended == False:
                        print("\n[OK] Found known message. Breaking...")
                        break                    
                    await look_for_dolphins(message, forward_dolphin_list)
                    start_time = "2025-01-14 10:00:00"
                    start_time_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    if message.date < start_time_datetime:
                        print(f"Message: {message.date}. Time limit: {start_time_datetime}. Found: {len(forward_list)}")
                        break
                    coordinates = get_coordinate_list_from_text(json.dumps(str(message)))
                    print(".", end="")
                    if not coordinates: 
                        continue
                    print("\n")
                    forward_list.append(copy.deepcopy(message))
                    link = message.link
                    if len(forward_list) > 10:
                        print(f"Found: {len(forward_list)}")
                        break
                    print(f'[OK] Coordinates found. Appending: {message.date}, {link}')

            forward_list = sorted(forward_list, key=lambda x: x.date)
            print(f"[OK] Chat look-up finished {datetime.now()}")
            print(f"[OK] Forwarding {len(forward_list)} messages ...")   
            print(str('-'*25))         

            for msg in forward_list:
                link = msg.link
                date = msg.date
                text = get_message_text(msg)
                topic = get_chat_topic(msg)
                send_text = f"{date}\n[{topic}]\n{link}\n{text}"
                coordinates = get_coordinate_list_from_text(json.dumps(str(msg)))
                send_text = send_text + "\n" + coordinates[0] + "\n"
                await app.send_message(target_group_id, send_text)
                await asyncio.sleep(5)          

            forward_dolphin_list = sorted(forward_dolphin_list, key=lambda x: x["date"])
            for msg in forward_dolphin_list:
                text = f'{msg["date"]} {msg["link"]}\n{msg["text"]}'
                await app.send_message(target_group_dolphins, text)
                await asyncio.sleep(5)   

            coordinate_storage.storage_flush()
            print(f"[OK] Forwarding done")   
            await asyncio.sleep(1*60)
d_list = ["дельф"]
re_exclude = r"штаб.{0,5}дельфин"

async def look_for_dolphins(message, forward_dolphin_list):
    message_dict = json.loads(str(message))
    message_dict["from"] = {}
    text = ""
    if message.text is not None:
        text = message.text
    if message.caption is not None:
        text = text + message.caption

    re_exclude_run = re.findall(re_exclude, text.lower())

    if "дельф" in  str(text).lower() and len (str(text)) < 500 and len(re_exclude_run) == 0:
        link = message.link
        date = message.date
        if link is None: return
        print(f"[..] Dolphin found {len(str(text))}, {link}")
        forward_dolphin_list.append({"date":date, "link":link, "text":text})
        #await app.send_message(target_group_dolphins, f"{date} {link}\n{text}")
        #await asyncio.sleep(5)  

if __name__ == "__main__":
    asyncio.run(main())
