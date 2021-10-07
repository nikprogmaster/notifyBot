import schedule, time
import datetime
import pandas
from threading import Thread
import telebot
import random
from time import sleep

import timetable
import search
import filemanager

BOT_TOKEN = '1870191359:AAG31P76p2xoTLcCGMt_dSnLn-sgQRp62ws'
BOT_INTERVAL = 3
BOT_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN)
leaders = []
allowed_leaders = []
super_leaders = []
reply_phrases = []


def send_message_in_day():
    global leaders
    leaders = timetable.read_timetable()
    current_date = datetime.datetime.today()
    chat_idenf = search.find_user_name(current_date.day, current_date.month, leaders)
    if chat_idenf != "":
        random_index = random.randrange(0, len(reply_phrases))
        random_phrase = reply_phrases[random_index]
        bot.send_message(int(chat_idenf), random_phrase)

    first_leader = search.find_first_leader_by_date(leaders)
    if first_leader is not None and (
            first_leader.date.day == current_date.day and first_leader.date.month == current_date.month):
        timetable.update_first_leader()


def send_message_the_day_before():
    global leaders
    leaders = timetable.read_timetable()
    tomorrow_date = datetime.datetime.today() + datetime.timedelta(days=1)
    chat_id = search.find_user_name(tomorrow_date.day, tomorrow_date.month, leaders)
    if chat_id != "":
        bot.send_message(int(chat_id), 'Не забудь, что завтра ты ведущий дневника МПшника! Подготовься.')
    last_leader = search.find_last_leader_date(leaders)
    if last_leader is not None and (
            last_leader.date.day == tomorrow_date.day and last_leader.date.month == tomorrow_date.month):
        timetable.update_schedule()


def cycle_scheduling():
    print("It is true")
    schedule.every().day.at("05:00").do(send_message_in_day)
    schedule.every().day.at("05:00").do(send_message_the_day_before)
    while True:
        schedule.run_pending()
        time.sleep(1)


def log(message):
    f = open('logs.txt', 'a', encoding="utf-8")
    f.write(str(datetime.datetime.now()) + ": " + message + "\n")
    f.close()


def bot_polling():
    global bot
    global allowed_leaders
    global super_leaders
    global reply_phrases
    print("Starting bot polling now")
    while True:
        try:
            log("New bot instance started")
            bot_actions()
            allowed_leaders = filemanager.init_leaders_names()
            super_leaders = filemanager.init_super_leaders()
            reply_phrases = filemanager.init_reply_phrases()
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex:
            log("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            log("Bot polling loop finished")
            break


def bot_actions():
    @bot.message_handler(commands=['start'], content_types=['text'])
    def send_welcome(message):
        if message.chat.type == "private":
            excel_data_df = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
            user_names = excel_data_df['User name'].tolist()
            print(message.chat.username)
            if (message.chat.username in allowed_leaders) and (message.chat.username not in user_names):
                search.find_leader(message.chat.username, leaders).reset_all_states()
                wr = pandas.DataFrame(
                    {'Name': [message.chat.first_name],
                     'User name': [message.chat.username],
                     'Chat id': [message.chat.id],
                     'Day': [1],
                     'Month': [1]})
                fr = pandas.concat([excel_data_df, wr], ignore_index=True)
                writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
                fr.to_excel(writer, 'Timetable', index=False)
                writer.save()
                bot.send_message(message.from_user.id,
                                 "Добро пожаловать! Я тебя узнал! Теперь ты есть в списке ведущих!")
            elif message.chat.username in user_names:
                bot.send_message(message.from_user.id, "А я уже тебя знаю! Ты записан как ведущий.")
            else:
                bot.send_message(message.from_user.id, "Приятно познакомиться! Но ты пока не ведущий ;)")

    @bot.message_handler(commands=['whoisleadertoday'], content_types=['text'])
    def who_is_leader_today(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in allowed_leaders:
            search.find_leader(message.from_user.username, leaders).reset_all_states()
            current_date = datetime.datetime.now() + datetime.timedelta(hours=3)
            print(current_date.day)
            for l in leaders:
                if l.date.day == current_date.day and l.date.month == current_date.month:
                    user_name = l.user_name
                    bot.send_message(message.chat.id, 'Сегодня дневник ведет @' + user_name)
                    break
            log("who_is_leader_today: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("who_is_leader_today: restricted")

    @bot.message_handler(commands=['wheniamleader'], content_types=['text'])
    def when_i_am_leader(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in allowed_leaders:
            search.find_leader(message.from_user.username, leaders).reset_all_states()
            for l in leaders:
                if l.user_name == message.from_user.username:
                    date = l.date
                    bot.send_message(message.chat.id, 'Ты ведешь дневник ' + str(date))
                    break
            log("when_i_am_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("when_i_am_leader: restricted")

    @bot.message_handler(commands=['schedule'], content_types=['text'])
    def get_schedule(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in allowed_leaders:
            search.find_leader(message.from_user.username, leaders).reset_all_states()
            result = ""
            for l in leaders:
                result += l.name + ' ' + str(l.date) + '\n'
            bot.send_message(message.chat.id, result)
            log("get_schedule: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("get_schedule: restricted")

    @bot.message_handler(commands=['addleader'], content_types=['text'])
    def add_leader(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.is_adding_user = True
                user.is_deleting_user = False
            bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("add_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("add_leader: restricted")

    @bot.message_handler(commands=['deleteleader'], content_types=['text'])
    def delete_leader(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.is_adding_user = False
                user.is_deleting_user = True
            bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("delete_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("delete_leader: restricted")

    @bot.message_handler(commands=['leaders'], content_types=['text'])
    def all_leaders(message):
        global leaders
        leaders = timetable.read_timetable()
        if message.from_user.username in allowed_leaders:
            result = ""
            for l in leaders:
                result += l.name + ' @' + l.user_name + '\n'
            bot.send_message(message.chat.id, result)
            log("all_leaders: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("all_leaders: restricted")

    @bot.message_handler(content_types=['text'])
    def handle_add_delete_leader_command(message):
        user = search.find_leader(message.from_user.username, leaders)
        if user is not None:
            if user.is_adding_user:
                if message.text.startswith("@"):
                    new_leader = message.text.replace("@", "")
                    filemanager.add_leader_to_allowed_leaders(new_leader, allowed_leaders)
                    user.is_adding_user = False
                    bot.send_message(message.chat.id,
                                     'Пользователь ' + message.text + " был успешно добавлен в список ведущих")
            elif user.is_deleting_user:
                if message.text.startswith("@"):
                    new_leader = message.text.replace("@", "")
                    filemanager.delete_leader_from_allowed_leaders(new_leader, allowed_leaders)
                    timetable.delete_from_schedule(new_leader, leaders)
                    user.is_deleting_user = False
                    bot.send_message(message.chat.id,
                                     'Пользователь ' + message.text + " был успешно удален из списка ведущих")
                    send_message_in_day()
                    send_message_the_day_before()


print("Bot is working")
t1 = Thread(target=bot_polling)
t1.daemon = True
t2 = Thread(target=cycle_scheduling)
t2.daemon = True
t1.start()
t2.start()

# Keep main program running while bot runs threaded
if __name__ == "__main__":
    while True:
        try:
            sleep(120)
        except KeyboardInterrupt:
            break
