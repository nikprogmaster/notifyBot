import time
import datetime
from threading import Thread
import telebot
from time import sleep
import scheduling
import timetable
import search
import filemanager
import validator

BOT_TOKEN = ""
BOT_INTERVAL = 3
BOT_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN)
leaders = []
allowed_leaders = []
super_leaders = []
reply_phrases = []
scheduling = scheduling.Scheduling(bot)


def log(message):
    f = open('res/logs.txt', 'a', encoding="utf-8")
    f.write(str(datetime.datetime.now()) + ": " + message + "\n")
    f.close()


def clear_user_states(username):
    leader = search.find_leader(username, leaders)
    if leader is not None:
        leader.set_states()


def bot_polling():
    global bot, allowed_leaders, super_leaders, reply_phrases, leaders
    print("Starting bot polling now")
    while True:
        try:
            log("New bot instance started")
            bot_actions()
            allowed_leaders = filemanager.init_leaders_names()
            super_leaders = filemanager.init_super_leaders()
            reply_phrases = filemanager.init_reply_phrases()
            scheduling.reply_phrases = reply_phrases
            scheduling.super_leaders = super_leaders
            leaders = timetable.read_timetable(super_leaders)
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
            user_names = list(map(lambda x: x.user_name, leaders))
            if (message.chat.username in allowed_leaders) and (message.chat.username not in user_names):
                timetable.add_new_leader(message)
                bot.send_message(message.from_user.id,
                                 "Добро пожаловать! Я тебя узнал! Теперь ты есть в списке ведущих!")
            elif message.chat.username in user_names:
                bot.send_message(message.from_user.id, "А я уже тебя знаю! Ты записан как ведущий.")
            else:
                bot.send_message(message.from_user.id, "Приятно познакомиться! Но ты пока не ведущий ;)")

    @bot.message_handler(commands=['whoisleadertoday'], content_types=['text'])
    def who_is_leader_today(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in allowed_leaders:
            clear_user_states(message.from_user.username)
            current_date = datetime.datetime.now() + datetime.timedelta(hours=3)
            user_name = search.find_username(current_date.day, current_date.month, leaders)
            bot.send_message(message.chat.id, 'Сегодня дневник ведет @' + user_name)
            log("who_is_leader_today: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("who_is_leader_today: restricted")

    @bot.message_handler(commands=['wheniamleader'], content_types=['text'])
    def when_i_am_leader(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in allowed_leaders:
            clear_user_states(message.from_user.username)
            for l in leaders:
                if l.user_name == message.from_user.username:
                    bot.send_message(message.chat.id, 'Ты ведешь дневник ' + str(l.date))
                    break
            log("when_i_am_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'Ты пока не ведущий.')
            log("when_i_am_leader: restricted")

    @bot.message_handler(commands=['schedule'], content_types=['text'])
    def get_schedule(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in allowed_leaders:
            clear_user_states(message.from_user.username)
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
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_adding=True)
                bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("add_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("add_leader: restricted")

    @bot.message_handler(commands=['deleteleader'], content_types=['text'])
    def delete_leader(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_deleting=True)
                bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("delete_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("delete_leader: restricted")

    @bot.message_handler(commands=['leaders'], content_types=['text'])
    def all_leaders(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders, needed_empty=True)
        if message.from_user.username in super_leaders:
            if message.chat.type == "private":
                search.find_leader(message.from_user.username, leaders).set_states()
                result = ""
                for nick in allowed_leaders:
                    result += '@' + nick + '\n'
                bot.send_message(message.chat.id, result)
                log("all_leaders: allowed")
            else:
                bot.send_message(message.chat.id, "Данная команда недоступна в чатах")
                log("all_leaders: restricted")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("all_leaders: restricted")

    @bot.message_handler(commands=['temporarilyremoveleader'], content_types=['text'])
    def temporarily_remove_leader(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_temporarily_deleting=True)
                bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("temporarily_remove_leader: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("temporarily_remove_leader: restricted")

    @bot.message_handler(commands=['changeleaderdate'], content_types=['text'])
    def change_leader_date(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders, needed_empty=True)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_changing_date=True)
                bot.send_message(message.chat.id, 'Укажи никнэйм человека в формате "@nickname"')
            log("change_leader_date: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("change_leader_date: restricted")

    @bot.message_handler(commands=['swapdates'], content_types=['text'])
    def swap_leaders_dates(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_swaping=True)
                bot.send_message(message.chat.id, 'Укажи никнэйм первого человека в формате "@nickname"')
            log("swap_leaders_dates: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("swap_leaders_dates: restricted")

    @bot.message_handler(commands=['turnonoff'], content_types=['text'])
    def turn_off_on_notifications(message):
        global schedule_thread, leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            if scheduling.stop_notifications:
                scheduling.stop_notifications = False
                schedule_thread = Thread(target=scheduling.run_scheduling)
                schedule_thread.daemon = True
                schedule_thread.start()
                bot.send_message(message.chat.id, 'Уведомления включены')
            else:
                time.sleep(2)
                scheduling.stop_notifications = True
                schedule_thread.join()
                bot.send_message(message.chat.id, 'Уведомления отключены')
            log("turn_off_on_notifications: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("turn_off_on_notifications: restricted")

    @bot.message_handler(commands=['transferrights'], content_types=['text'])
    def transfer_rights_of_bot(message):
        global leaders
        leaders = timetable.read_timetable(super_leaders)
        if message.from_user.username in super_leaders:
            user = search.find_leader(message.from_user.username, leaders)
            if user is not None:
                user.set_states(is_transfering_rights=True)
                bot.send_message(message.chat.id, 'Внимание! При передаче прав суперадмина, у вас пропадет '
                                                  'возможность менять ведущих, даты, и др. ')

                bot.send_message(message.chat.id, 'Укажи никнэйм нового суперадмина в формате @nickname ')
            log("transfer_rights_of_bot: allowed")
        else:
            bot.send_message(message.chat.id, 'У тебя недостаточно прав')
            log("transfer_rights_of_bot: restricted")

    @bot.message_handler(content_types=['text'])
    def handle_user_input(message):
        global leaders
        user = search.find_leader(message.from_user.username, leaders)
        if user is not None and user.superuser_settings is not None:
            if user.superuser_settings.is_adding_user:
                if message.text.startswith("@"):
                    new_leader = message.text.replace("@", "")
                    filemanager.add_leader_to_allowed_leaders(new_leader, allowed_leaders)
                    user.set_states()
                    bot.send_message(message.chat.id,
                                     'Пользователь ' + message.text + " был успешно добавлен в список ведущих")
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')
            elif user.superuser_settings.is_deleting_user:
                if message.text.startswith("@"):
                    new_leader = message.text.replace("@", "")
                    user_in_database = search.find_leader(new_leader, leaders)
                    if user_in_database is None and new_leader not in allowed_leaders:
                        bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                    else:
                        filemanager.delete_leader_from_allowed_leaders(new_leader, allowed_leaders)
                        if user_in_database is not None:
                            timetable.delete_forever(new_leader, leaders)
                        user.set_states()
                        bot.send_message(message.chat.id,
                                         'Пользователь ' + message.text + " был успешно удален из списка ведущих")
                        #оповестить пользователей, что даты изменились
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')
            elif user.superuser_settings.is_temporarily_deleting:
                if message.text.startswith("@"):
                    new_leader = message.text.replace("@", "")
                    if search.find_leader(new_leader, leaders) is None:
                        bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                    else:
                        timetable.delete_from_schedule(new_leader, leaders)
                        user.set_states()
                        bot.send_message(message.chat.id, 'Пользователь ' + message.text + " был убран из расписания")
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')
            elif user.superuser_settings.is_transfering_rights:
                if message.text.startswith("@"):
                    new_super_leader = message.text.replace("@", "")
                    if search.find_leader(new_super_leader, leaders) is None:
                        bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                    else:
                        filemanager.add_super_leader(new_super_leader, super_leaders)
                        filemanager.remove_super_leader(user.user_name, super_leaders)
                        user.set_states()
                        bot.send_message(message.chat.id, 'Вы передали права суперадмина ' + message.text)
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')
            elif user.superuser_settings.is_changing_date:
                if message.text.startswith("@"):
                    user.superuser_settings.changing_date_leader = message.text.replace("@", "")
                    if search.find_leader(user.superuser_settings.changing_date_leader, leaders) is None:
                        bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                    else:
                        bot.send_message(message.chat.id, 'Введите новую дату в формате дд.мм (например 25.12)')
                elif validator.validate(message.text):
                    if timetable.check_for_same_date(message.text):
                        timetable.change_leader_date(user.superuser_settings.changing_date_leader, message.text)
                        user.set_states()
                        bot.send_message(message.chat.id,
                                         'Дата для пользователя ' + '@' + user.superuser_settings.changing_date_leader + ' была изменена')
                    else:
                        bot.send_message(message.chat.id,
                                         'Эта дата уже занята. Выберите другую или воспользуйся командой "Поменять местами даты ведущих"')
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')
            elif user.superuser_settings.is_swaping:
                if message.text.startswith("@"):
                    leader = message.text.replace("@", "")
                    if len(user.superuser_settings.swaping_leaders) == 0:
                        if search.find_leader(leader, leaders) is None:
                            bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                        else:
                            user.superuser_settings.swaping_leaders.append(leader)
                            bot.send_message(message.chat.id, 'Укажи никнэйм второго человека в формате "@nickname"')
                    else:
                        if search.find_leader(leader, leaders) is None:
                            bot.send_message(message.chat.id, 'Ведущего с ником ' + message.text + " не существует")
                        else:
                            user.superuser_settings.swaping_leaders.append(leader)
                            timetable.swap_leaders_dates(user.superuser_settings.swaping_leaders[0],
                                                         user.superuser_settings.swaping_leaders[1])
                            user.set_states()
                            bot.send_message(message.chat.id, 'Даты были успешно изменены')
                else:
                    bot.send_message(message.chat.id, 'Вы ввели что-то некорректное. Попробуйте еще раз')


print("Bot is working")
polling_thread = Thread(target=bot_polling)
polling_thread.daemon = True
schedule_thread = Thread(target=scheduling.run_scheduling)
schedule_thread.daemon = True
polling_thread.start()
schedule_thread.start()

# Keep main program running while bot runs threaded
if __name__ == "__main__":
    while True:
        try:
            sleep(120)
        except KeyboardInterrupt:
            break
