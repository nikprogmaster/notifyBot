
def find_last_leader_date(leaders):
    leaders.sort(key=lambda l: l.date)
    if len(leaders) > 0:
        return leaders[len(leaders) - 1]


def find_first_leader_by_date(leaders):
    leaders.sort(key=lambda l: l.date)
    if len(leaders) > 0:
        return leaders[0]


def find_user_name(day, month, leaders):
    chat_idenf = ""
    for leader in leaders:
        if leader.date.day == day and leader.date.month == month:
            chat_idenf = leader.chat_id
    return chat_idenf


def find_leader(username, leaders):
    for l in leaders:
        if l.user_name == username:
            return l
