import schedule, time
import datetime
import pandas
import leader
from threading import Thread
import telebot
import random
from time import sleep

BOT_TOKEN = '1870191359:AAG31P76p2xoTLcCGMt_dSnLn-sgQRp62ws'
BOT_INTERVAL = 3
BOT_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN)
leaders = []
allowed_leaders = []
reply_phrases = []


def read_timetable():
    global leaders
    leaders = []
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()
    print(names_list)

    for i in range(0, len(names_list)):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        leaders.append(l)


def find_last_leader_date():
    leaders.sort(key=lambda leader: leader.date)
    if len(leaders) > 0:
        return leaders[len(leaders)-1]


def find_user_name(day, month):
    chat_id = ""
    for leader in leaders:
        if leader.date.day == day and leader.date.month == month:
            chat_id = leader.chat_id
    return chat_id


def send_message_in_day():
    read_timetable()
    current_date = datetime.datetime.today()
    chat_id = find_user_name(current_date.day, current_date.month)
    if chat_id != "":
        random_index = random.randrange(0, len(reply_phrases))
        random_phrase = reply_phrases[random_index]
        bot.send_message(int(chat_id), random_phrase)
    last_leader = find_last_leader_date()
    if last_leader is not None and (last_leader.date.day == current_date.day and last_leader.date.month == current_date.month):
        update_last_leader()


def send_message_the_day_before():
    read_timetable()
    tomorrow_date = datetime.datetime.today() + datetime.timedelta(days=1)
    chat_id = find_user_name(tomorrow_date.day, tomorrow_date.month)
    if chat_id != "":
        bot.send_message(int(chat_id), 'Не забудь, что завтра ты ведущий дневника МПшника! Подготовься.')
    last_leader = find_last_leader_date()
    if last_leader is not None and (last_leader.date.day == tomorrow_date.day and last_leader.date.month == tomorrow_date.month):
        update_schedule()


def update_schedule():
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()

    for i in range(0, len(names_list) - 1):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        l.append_date(len(names_list))
        days_list[i] = l.date.day
        month_list[i] = l.date.month

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()


def update_last_leader():
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()
    length = len(names_list)
    l = leader.Leader(names_list[length-1], user_names_list[length-1], chat_ids_list[length-1], days_list[length-1], month_list[length-1])
    l.append_date(len(names_list))
    days_list[length-1] = l.date.day
    month_list[length-1] = l.date.month

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()


def cycle_scheduling():
    print("It is true")
    schedule.every().day.at("05:00").do(send_message_in_day)
    schedule.every().day.at("05:00").do(send_message_the_day_before)
    while True:
        schedule.run_pending()
        time.sleep(1)


def init_leaders_names():
    f = open('leaders_names.txt', 'r')
    global allowed_leaders
    for line in f:
        allowed_leaders.append(line)
    allowed_leaders = [line.rstrip() for line in allowed_leaders]
    f.close()


def init_reply_phrases():
    f = open('reply_phrases.txt', 'r', encoding="utf-8")
    global reply_phrases
    for line in f:
        reply_phrases.append(line)
    reply_phrases = [line.rstrip() for line in reply_phrases]
    f.close()


def log(message):
    f = open('logs.txt', 'a', encoding="utf-8")
    f.write(str(datetime.datetime.now()) + ": " + message + "\n")
    f.close()


def bot_polling():
    global bot
    print("Starting bot polling now")
    while True:
        try:
            log("New bot instance started")
            bot_actions()
            init_leaders_names()
            init_reply_phrases()
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
        read_timetable()
        if message.from_user.username in allowed_leaders:
            current_date = datetime.datetime.now() + datetime.timedelta(hours=3)
            print(current_date.day)
            for l in leaders:
                if l.date.day == current_date.day and l.date.month == current_date.month:
                    user_name = l.user_name
                    bot.send_message(message.chat.id, 'Сегодня дневник ведет @' + user_name)
                    break
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')

    @bot.message_handler(commands=['wheniamleader'], content_types=['text'])
    def when_i_am_leader(message):
        read_timetable()
        if message.from_user.username in allowed_leaders:
            for l in leaders:
                if l.user_name == message.from_user.username:
                    date = l.date
                    bot.send_message(message.chat.id, 'Ты ведешь дневник ' + str(date))
                    break
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')

    @bot.message_handler(commands=['schedule'], content_types=['text'])
    def get_schedule(message):
        read_timetable()
        if message.from_user.username in allowed_leaders:
            result = ""
            for l in leaders:
                result += l.name + ' ' + str(l.date) + '\n'
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')


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


