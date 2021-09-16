import schedule, time
import datetime
import pandas
import leader
from threading import Thread
import telebot
import random

bot = telebot.TeleBot('1870191359:AAG31P76p2xoTLcCGMt_dSnLn-sgQRp62ws')
leaders = []
allowed_leaders = []
reply_phrases = []


def read_timetable():
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
    print(leaders)


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
            bot.send_message(message.from_user.id, "Добро пожаловать! Я тебя узнал! Теперь ты есть в списке ведущих!")
        elif message.chat.username in user_names:
            bot.send_message(message.from_user.id, "А я уже тебя знаю! Ты записан как ведущий.")
        else:
            bot.send_message(message.from_user.id, "Приятно познакомиться! Но ты пока не ведущий ;)")


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
    new_days_list = []
    new_month_list = []

    for i in range(0, len(names_list)):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        l.append_date(len(names_list))
        new_days_list.append(l.date.day)
        new_month_list.append(l.date.month)

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': new_days_list,
         'Month': new_month_list})
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


def start_bot():
    bot.polling(non_stop=True, interval=1)


print("Bot is working")

init_leaders_names()
init_reply_phrases()

t1 = Thread(target=start_bot)
t2 = Thread(target=cycle_scheduling)
t1.start()
t2.start()

