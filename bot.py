import schedule, time
import telebot
import datetime
import pandas
import leader
from multiprocessing import *

bot = telebot.TeleBot('1870191359:AAG31P76p2xoTLcCGMt_dSnLn-sgQRp62ws')
leaders = []
allowed_leaders = []

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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == "private":
        excel_data_df = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
        user_names = excel_data_df['User name'].tolist()
        if allowed_leaders.__contains__(message.chat.username) and not user_names.__contains__(message.chat.username):
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
        else:
            bot.send_message(message.from_user.id, "Приятно познакомиться! Но ты пока не ведущий ;)")


def find_user_name(day, month):
    chat_id = ""
    for leader in leaders:
        if leader.date.day == day and leader.date.month == month:
            chat_id = leader.chat_id
    return chat_id


def send_message():
    read_timetable()
    current_date = datetime.datetime.today()
    chat_id = find_user_name(current_date.day, current_date.month)
    print(current_date)
    bot.send_message(int(chat_id), 'Hello')


def cycle_scheduling():
    while True:
        schedule.run_pending()
        time.sleep(1)


def init_leaders_names():
    f = open('leaders_names.txt', 'r')
    for line in f:
        allowed_leaders.append(line)
    f.close()


print("Bot is working")

schedule.every().day.at("22:42").do(send_message)
Process(target=cycle_scheduling()).start()

bot.polling(none_stop=True, interval=0)


