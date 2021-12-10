import datetime


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d.%m')
        return True
    except ValueError:
        return False

