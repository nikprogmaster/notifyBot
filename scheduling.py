import timetable
import datetime
import search
import random
import schedule
import time
from threading import Thread

notify_time = "05:00"
update_last_leader_time = "20:59"


class Scheduling:

    def __init__(self, bot):
        self.bot = bot
        self.super_leaders = []
        self.reply_phrases = []
        self.stop_notifications = False
        self.updating_scheduler = None
        self.sending_scheduler = None

    def send_message_in_day(self):
        leaders = timetable.read_timetable(self.super_leaders)
        current_date = datetime.datetime.today() + datetime.timedelta(hours=3)
        chat_idenf = search.find_user_chatid(current_date.day, current_date.month, leaders)
        if chat_idenf != "" and not self.stop_notifications:
            random_index = random.randrange(0, len(self.reply_phrases))
            random_phrase = self.reply_phrases[random_index]
            self.bot.send_message(int(chat_idenf), random_phrase)

        first_leader = search.find_first_leader_by_date(leaders)
        if first_leader is not None and (
                first_leader.date.day == current_date.day and first_leader.date.month == current_date.month):
            thread = Thread(target=self.update_first_leader)
            thread.daemon = True
            thread.start()

    def send_message_the_day_before(self):
        leaders = timetable.read_timetable(self.super_leaders)
        tomorrow_date = datetime.datetime.today() + datetime.timedelta(days=1)
        chat_id = search.find_user_chatid(tomorrow_date.day, tomorrow_date.month, leaders)
        if chat_id != "" and not self.stop_notifications:
            self.bot.send_message(int(chat_id), 'Не забудь, что завтра ты ведущий дневника МПшника! Подготовься.')
        # последний обновляемый ведущий
        last_leader = search.find_last_leader_date(leaders)
        if last_leader is not None and (
                last_leader.date.day == tomorrow_date.day and last_leader.date.month == tomorrow_date.month):
            timetable.update_schedule()
            thread = Thread(target=self.update_first_leader)
            thread.daemon = True
            thread.start()

    def update_first_leader(self):
        updating_scheduler = schedule.Scheduler()
        updating_scheduler.every().day.at(update_last_leader_time).do(self.run_updating)
        while True:
            updating_scheduler.run_pending()
            # если нет тасок в scheduler, то выходим из цикла
            if len(updating_scheduler.jobs) == 0:
                break
            time.sleep(1)

    def run_updating(self):
        timetable.update_first_leader()
        return schedule.CancelJob

    def run_scheduling(self):
        sending_scheduler = schedule.Scheduler()
        sending_scheduler.every().day.at(notify_time).do(self.send_message_in_day)
        sending_scheduler.every().day.at(notify_time).do(self.send_message_the_day_before)
        while True:
            sending_scheduler.run_pending()
            time.sleep(1)

