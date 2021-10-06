import datetime


class Leader:

    def __init__(self, name, user_name, chat_id, day, month):
        current_date = datetime.datetime.today()
        self.name = name
        self.user_name = user_name
        self.chat_id = chat_id
        self.date = datetime.date(current_date.year, month, day)
        self.is_adding_user = False
        self.is_deleting_user = False

    def append_date(self, days):
        self.date = self.date + datetime.timedelta(days=days)

    def decrease_date(self, days):
        self.date = self.date - datetime.timedelta(days=days)

