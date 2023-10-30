import bson
import datetime
import asyncio
import json
import sys
import logging
import pymongo

from datetime import datetime
from dateutil.relativedelta import relativedelta
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types


"""Запись данных с bson файла в mongodb"""
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['admin']
coll = db['coll']

# with open('sample_collection.bson', 'rb') as f:
#     bson_data = bson.decode_all(f.read())
#
# coll.insert_many(bson_data)
"""######################################"""


bot = Bot(token="6719983801:AAFWW8Rq_4GhqUFpZ8Sv-NkTRYT_izvJIBg")
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(text='Дарова')


@dp.message_handler(content_types=['any'])
async def msg(message: types.Message):
    start_date_format = "%Y-%m-%dT%H:%M:%S"
    date_format = "%Y-%m-%d %H:%M:%S"
    insert_value = eval(message.text)
    new_dt_from = datetime.strptime(str(datetime.strptime(insert_value['dt_from'], start_date_format)), date_format)
    new_dt_upto = datetime.strptime(str(datetime.strptime(insert_value['dt_upto'], start_date_format)), date_format)
    group_type = insert_value['group_type']

    full_dates = []
    for i in coll.find():
        if new_dt_from <= i['dt'] <= new_dt_upto:
            full_dates.append(i)

    dataset = []
    labels = []

    if group_type == 'hour':
        now = new_dt_from
        while now <= new_dt_upto:
            res = 0
            for i in full_dates:
                if i['dt'].year == now.year and i['dt'].month == now.month and i['dt'].day == now.day and i['dt'].hour == now.hour:
                    res += i['value']
            dataset.append(res)
            labels.append(now.strftime(start_date_format))
            now += relativedelta(hours=1)
    elif group_type == 'day':
        now = new_dt_from
        while now <= new_dt_upto:
            res = 0
            for i in full_dates:
                if i['dt'].year == now.year and i['dt'].month == now.month and i['dt'].day == now.day:
                    res += i['value']
            dataset.append(res)
            labels.append(now.strftime(start_date_format))
            now += relativedelta(days=1)
    elif group_type == 'month':
        now = new_dt_from
        while now <= new_dt_upto:
            res = 0
            for i in full_dates:
                if i['dt'].year == now.year and i['dt'].month == now.month:
                    res += i['value']
            dataset.append(res)
            labels.append(now.strftime(start_date_format))
            now += relativedelta(months=1)

    diction = json.dumps({"dataset": dataset, "labels": labels})
    await message.answer(diction)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())