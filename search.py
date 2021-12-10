import math


def find_last_leader_date(leaders):
    leaders.sort(key=lambda l: l.date)
    if len(leaders) > 0:
        return leaders[len(leaders) - 1]


def find_first_leader_by_date(leaders):
    leaders.sort(key=lambda l: l.date)
    if len(leaders) > 0:
        return leaders[0]


def find_user_chatid(day, month, leaders):
    chat_idenf = ""
    for leader in leaders:
        if leader.date.day == day and leader.date.month == month:
            chat_idenf = leader.chat_id
            break
    return chat_idenf


def find_username(day, month, leaders):
    username = ""
    for leader in leaders:
        if leader.date.day == day and leader.date.month == month:
            username = leader.user_name
            break
    return username


def find_leader(username, leaders):
    for l in leaders:
        if l.user_name == username:
            return l


def find_empty_leaders(days_list, month_list):
    index_array = []
    for i in range(0, len(days_list)):
        if math.isnan(days_list[i]):
            index_array.append(i)
    for i in range(0, len(month_list)):
        if math.isnan(month_list[i]) and i not in index_array:
            index_array.append(i)
    return index_array


