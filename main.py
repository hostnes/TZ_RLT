# import pymongo
# import bson
# import datetime
#
# client = pymongo.MongoClient("mongodb://localhost:27017")
# db = client['admin']
# coll = db['coll']
#
# with open('sample_collection.bson', 'rb') as f:
#     bson_data = bson.decode_all(f.read())
#
# # print(bson.encode(bson_data))
# # data = bson.decode(bson_data)
#
# coll.insert_many(bson_data)
import asyncio
import sys

import pymongo

from datetime import datetime

import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from dateutil.relativedelta import relativedelta
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher, types

from aiogram.dispatcher.filters.state import State, StatesGroup

from state import SendMessage

bot = Bot(token="6719983801:AAFWW8Rq_4GhqUFpZ8Sv-NkTRYT_izvJIBg")
dp = Dispatcher(bot, storage=MemoryStorage())

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['admin']
coll = db['coll']


@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    await message.answer(text='Дарова')
    await state.set_state(SendMessage.get_message.state)


@dp.message_handler(state=SendMessage.get_message)
async def msg(message: types.Message, state: FSMContext):
    date_format = "%Y-%m-%dT%H:%M:%S"
    print(message.from_user.id)

    try:
        insert_value = eval(message.text)

        dt_from = datetime.strptime(insert_value['dt_from'], date_format)
        dt_upto = datetime.strptime(insert_value['dt_upto'], date_format)
        group_type = insert_value['group_type']

        date_format = "%Y-%m-%d %H:%M:%S"

        new_dt_from = datetime.strptime(str(dt_from), date_format)
        new_dt_upto = datetime.strptime(str(dt_upto), date_format)

        full_dates = []
        for i in coll.find():
            if new_dt_from <= i['dt']:
                if i['dt'] <= new_dt_upto:
                    # print(i['dt'])
                    full_dates.append(i)

        dataset = []
        labels = []

        if group_type == 'day':
            now = new_dt_from
            while True:
                res = 0
                if now <= new_dt_upto:
                    for i in full_dates:
                        if i['dt'].year == now.year:
                            if i['dt'].month == now.month:
                                if i['dt'].day == now.day:
                                 res += i['value']
                    dataset.append(res)
                    labels.append(str(now))
                    now += relativedelta(days=1)
                else:
                    break

        if group_type == 'month':
            now = new_dt_from
            while True:
                res = 0
                if now <= new_dt_upto:
                    for i in full_dates:
                        if i['dt'].year == now.year:
                            if i['dt'].month == now.month:
                                res += i['value']
                    dataset.append(res)
                    labels.append(str(now))
                    now += relativedelta(months=1)
                else:
                    break

        if group_type == 'hour':
            now = new_dt_from
            while True:
                res = 0
                if now <= new_dt_upto:
                    for i in full_dates:
                        if i['dt'].year == now.year:
                            if i['dt'].month == now.month:
                                if i['dt'].day == now.day:
                                    if i['dt'].hour == now.hour:
                                        res += i['value']
                    dataset.append(res)
                    labels.append(str(now))
                    now += relativedelta(hours=1)
                else:
                    break

        diction = {'dataset': dataset, 'labels': labels}
        await message.answer(str(diction))
    except:
        await message.answer('что то не так')




async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

