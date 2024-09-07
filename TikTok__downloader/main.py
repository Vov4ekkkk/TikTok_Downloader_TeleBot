import os, configparser, requests
from aiogram import Dispatcher, types, Bot
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tiktok_downloader import snaptik
import sqlite3
import logging


config = configparser.ConfigParser()
config.read("settings.ini")
admin_id = config['bot']['admin_id'].split()
TOKEN = '7231651529:AAGotzsy9stBBQQdWPgmO3SLPXTmp5Jxzow'

with sqlite3.connect('database.db') as con:
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM users')
    except:
        cur.execute('CREATE TABLE users(user_id INT)')
    try:
        cur.execute('SELECT * FROM stats')
    except:
        cur.execute('CREATE TABLE stats(download_count INT)')
        cur.execute('INSERT INTO stats VALUES(0)')
if con:
    con.commit()
    con.close()

def new_user(user_id):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        user = cur.execute(f'SELECT * FROM users WHERE user_id={user_id}').fetchall()
        if len(user) == 0:
            cur.execute(f'INSERT INTO users VALUES({user_id})')
            con.commit()
        else:
            pass
    if con:
        con.close()

def get_users_count():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = cur.execute('SELECT * FROM users').fetchall()
    if con:
        con.close()
    return result

def get_users():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = []
        for user in cur.execute('SELECT * FROM users').fetchall():
            result.append(user[0])
    if con:
        con.close()
    return result

def add_new_download():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        new = int(cur.execute('SELECT * FROM stats').fetchone()[0])+1
        cur.execute(f'UPDATE stats SET download_count={new}')
        con.commit()
    if con:
        con.close()

def get_downloads():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        result = int(cur.execute('SELECT * FROM stats').fetchone()[0])
    if con:
        con.close()
    return result

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def download_video(video_url, name):
    r = requests.get(video_url, allow_redirects=True)
    content_type = r.headers.get('content-type')
    if content_type == 'video/mp4':
        open(f'./videos/video{name}.mp4', 'wb').write(r.content)
    else:
        pass


if not os.path.exists('videos'):
    os.makedirs('videos')

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    new_user(message.chat.id)
    await bot.send_message(chat_id=message.chat.id,
                           text='Добрий день!\n\nЯ помагаю зкачувати відео без водяного знаку з TikTok.\nПросто відправ мені посилання на відео. ')

@dp.message_handler(commands='send')
async def command_letter(message):
    if str(message.chat.id) in admin_id:
        await bot.send_message(message.chat.id, f"*Розсилка Розпочалсь \nБот повідомить коли закінчиться розсилка*", parse_mode='Markdown')
        receive_users, block_users = 0, 0
        text = message.text.split()
        if len(text) > 1:
            try:
                lst = get_users()
                cache = ''
                for string in text[1::]:
                    cache += string+' '
                for user in lst:
                    await bot.send_message(user, cache)
                    receive_users += 1
            except:
                 block_users += 1
        await bot.send_message(message.chat.id, f"*Розсилка була завершена *\n"
                                                              f"Получили повідомлення: *{receive_users}*\n"
                                                              f"Заблокували бота: *{block_users}*", parse_mode='Markdown')

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Скопіюй посилання на відео в TikTok і відправ її до мене:')


@dp.message_handler(commands=['stats'])
async def statistika_command(message: types.Message):
    if str(message.chat.id) in admin_id:
        sk = get_downloads()
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Кількість користувачів: {len(get_users_count())} \nВсього запитів: {sk}')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Команда для адміністраторів')

@dp.message_handler(commands=['send'])
async def statistika_command(message: types.Message):
    if str(message.chat.id) in admin_id:
        sk = get_downloads()
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Кількість користувачів: {len(get_users_count())} \nВсього запитів: {sk}')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Команда для адміністраторів')


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    new_user(message.chat.id)
    if message.text.startswith('https://www.tiktok.com') or message.text.startswith(
            'https://vm.tiktok.com') or message.text.startswith('http://vm.tiktok.com'):
        await bot.send_message(chat_id=message.chat.id, text='Будь ласка, почекайте...')
        video_url = message.text
        try:
            media_list = snaptik(video_url)
            print("Type of media_list:", type(media_list))
            print("media_list:", media_list)  # Виводимо весь список або об'єкт, який повертається

            if isinstance(media_list, list) and len(media_list) > 0:
                # Перевірте структуру першого елемента списку
                media = media_list[0]
                print("Type of media:", type(media))
                print("media:", media)

                # Завантаження відео (переконайтеся, що `media` має потрібний метод)
                if hasattr(media, 'download'):
                    media.download(f"./videos/result_{message.from_user.id}.mp4")
                    path = f'./videos/result_{message.from_user.id}.mp4'
                    add_new_download()
                    # await bot.delete_message(message.chat.id, message.message_id)
                    with open(f'./videos/result_{message.from_user.id}.mp4', 'rb') as file:
                        await bot.send_video(
                            chat_id=message.chat.id,
                            video=file.read(),
                            caption='Скачано в @your'
                        )
                    os.remove(path)
                else:
                    print("Об'єкт media не має методу 'download'.")
                    await bot.send_message(chat_id=message.chat.id,
                                           text='Помилка при скачуванню, неправильно надане посилання, відео було видалено або я его не найшов.')
            else:
                print("media_list не є списком або список порожній.")
                await bot.send_message(chat_id=message.chat.id,
                                       text='Помилка при скачуванню, неправильно надане посилання, відео було видалено або я его не найшов.')
        except Exception as e:
            print("Помилка:", e)
            await bot.send_message(chat_id=message.chat.id,
                                   text='Помилка при скачуванню, неправильно надане посилання, відео було видалено або я его не найшов.')
    else:
        await bot.send_message(chat_id=message.chat.id, text='Я тебя не зрозумів, відправ мені посилання на відео TikTok.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)