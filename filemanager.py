
def init_leaders_names():
    allowed_leaders = []
    f = open('leaders_names.txt', 'r')
    for line in f:
        allowed_leaders.append(line)
    allowed_leaders = [line.rstrip() for line in allowed_leaders]
    f.close()
    return allowed_leaders


def init_super_leaders():
    super_leaders = []
    f = open('super_leaders.txt', 'r')
    for line in f:
        super_leaders.append(line)
    super_leaders = [line.rstrip() for line in super_leaders]
    f.close()
    return super_leaders


def init_reply_phrases():
    reply_phrases = []
    f = open('reply_phrases.txt', 'r', encoding="utf-8")
    for line in f:
        reply_phrases.append(line)
    reply_phrases = [line.rstrip() for line in reply_phrases]
    f.close()
    return reply_phrases


def add_leader_to_allowed_leaders(username, allowed_leaders):
    if username not in allowed_leaders:
        f = open('leaders_names.txt', 'a')
        f.write(str(username) + "\n")
        f.close()
        allowed_leaders.append(username)


def delete_leader_from_allowed_leaders(username, allowed_leaders):
    f = open('leaders_names.txt', 'w')
    for l in allowed_leaders:
        if l != username:
            f.write(l + "\n")
    f.close()
    allowed_leaders.remove(username)