import datetime
import math


class Leader:

    def __init__(self, name, user_name, chat_id, day, month, superuser_settings=None):
        current_date = datetime.datetime.today()
        self.name = name
        self.user_name = user_name
        self.chat_id = chat_id
        if math.isnan(day) or math.isnan(month):
            self.date = datetime.datetime.today()
        else:
            self.date = datetime.date(current_date.year, int(month), int(day))
        self.superuser_settings = superuser_settings

    def append_date(self, days):
        self.date = self.date + datetime.timedelta(days=days)

    def decrease_date(self, days):
        self.date = self.date - datetime.timedelta(days=days)

    def set_states(self, is_deleting=False, is_adding=False, is_temporarily_deleting=False, is_changing_date=False,
                   is_swaping=False, is_transfering_rights=False):
        if self.superuser_settings is not None:
            self.superuser_settings.set_states(
                is_deleting, is_adding, is_temporarily_deleting, is_changing_date, is_swaping, is_transfering_rights)

