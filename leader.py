import datetime


class Leader:
    name = ""
    user_name = ""
    chat_id = ""
    date = datetime.datetime.today()

    def __init__(self, name, user_name, chat_id, day, month):
        current_date = datetime.datetime.today()
        self.name = name
        self.user_name = user_name
        self.chat_id = chat_id
        self.date = datetime.date(current_date.year, month, day)
