import leader
import pandas
import search
import superuser_settings
import datetime
import quick_sort
import math

names_list = []
user_names_list = []
chat_ids_list = []
days_list = []
month_list = []


def add_new_leader(message):
    excel_data_df = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    wr = pandas.DataFrame(
        {'Name': [message.chat.first_name],
         'User name': [message.chat.username],
         'Chat id': [message.chat.id],
         'Day': [1],
         'Month': [1]})
    fr = pandas.concat([excel_data_df, wr], ignore_index=True)
    writer = pandas.ExcelWriter('res/leading.xlsx', engine='xlsxwriter')
    fr.to_excel(writer, 'Timetable', index=False)
    writer.save()


def read_timetable(superusers, needed_empty=False):
    leaders = []
    _read_internal(needed_empty)

    for i in range(0, len(names_list)):
        su_settings = None
        if user_names_list[i] in superusers:
            su_settings = superuser_settings.SuperuserSettings()
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], int(days_list[i]), int(month_list[i]),
                          su_settings)
        leaders.append(l)
    return leaders


def update_schedule():
    _read_internal()

    # обновляем всех ведущих, кроме последних двух
    for i in range(0, len(names_list) - 2):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        l.append_date(len(names_list))
        days_list[i] = l.date.day
        month_list[i] = l.date.month

    _save_changes_in_excel()


def update_first_leader():
    """
    Обновляем первого по дате ведущего
    """
    _read_internal()
    # сортируем на случай того, что кто-то поменял даты ведущим во время 2х дневного обновления расписания
    _sort_timetable()

    first_leader_index = 0
    l = leader.Leader(names_list[first_leader_index], user_names_list[first_leader_index],
                      chat_ids_list[first_leader_index], days_list[first_leader_index], month_list[first_leader_index])
    l.append_date(len(names_list))
    days_list[first_leader_index] = l.date.day
    month_list[first_leader_index] = l.date.month

    _sort_timetable()
    _save_changes_in_excel()


def delete_forever(username, leaders):
    _read_internal()

    user_index = 0
    for i in user_names_list:
        if i == username:
            user_index = user_names_list.index(i)

    if user_index != 0:
        start_index = 0
        if leaders[0].date < leaders[len(leaders) - 1].date:
            start_index = user_index + 1

        for i in range(start_index, len(user_names_list)):
            if i != user_index:
                l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
                l.decrease_date(1)
                days_list[i] = l.date.day
                month_list[i] = l.date.month

        names_list.pop(user_index)
        user_names_list.pop(user_index)
        chat_ids_list.pop(user_index)
        days_list.pop(user_index)
        month_list.pop(user_index)

    _save_changes_in_excel()


def delete_from_schedule(username, leaders):
    _read_internal()

    user_index = 0
    for i in user_names_list:
        if i == username:
            user_index = user_names_list.index(i)

    if user_index != 0:
        start_index = 0
        if leaders[0].date < leaders[len(leaders) - 1].date:
            start_index = user_index + 1

        for i in range(start_index, len(user_names_list)):
            if i != user_index:
                l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
                l.decrease_date(1)
                days_list[i] = l.date.day
                month_list[i] = l.date.month

        days_list[user_index] = None
        month_list[user_index] = None

    _save_changes_in_excel()


def change_leader_date(username, new_date):
    _read_internal(True)
    user_index = -1
    # ищем индекс нужного пользователя
    for i in user_names_list:
        if i == username:
            user_index = user_names_list.index(i)

    if user_index != -1:
        # парсим строку с датой
        day = int(new_date.split('.')[0])
        month = int(new_date.split('.')[1])
        # назначаем дату для найденного пользователя
        days_list[user_index] = day
        month_list[user_index] = month

        # сохраняем изменения перед тем, как отсортировать
        _save_changes_in_excel()

        # читаем таблицу (но без пустых записей), сортируем и сохраняем
        _read_internal(False)
        _sort_timetable()
        _save_changes_in_excel()


def swap_leaders_dates(first_leader, second_leader):
    _read_internal()
    first_leader_index = -1
    second_leader_index = -1
    for i in range(0, len(user_names_list)):
        if user_names_list[i] == first_leader:
            first_leader_index = i
        if user_names_list[i] == second_leader:
            second_leader_index = i

    if first_leader_index != -1 and second_leader_index != -1:
        swap = days_list[first_leader_index]
        days_list[first_leader_index] = days_list[second_leader_index]
        days_list[second_leader_index] = swap
        swap = month_list[first_leader_index]
        month_list[first_leader_index] = month_list[second_leader_index]
        month_list[second_leader_index] = swap

    _sort_timetable()
    _save_changes_in_excel()


def check_for_same_date(new_date):
    _read_internal(False)
    day = int(new_date.split('.')[0])
    month = int(new_date.split('.')[1])
    for i in range(len(days_list)):
        if days_list[i] == day and month_list[i] == month:
            return False
    return True


def _sort_timetable():
    date_list = []

    for i in range(len(days_list)):
        item = datetime.date.today()
        date_list.append(item.replace(month=int(month_list[i]), day=int(days_list[i])))

    if len(date_list) != 0:
        sort = quick_sort.QuickSort(names_list, user_names_list, chat_ids_list, days_list, month_list)
        sort.quick_sort(date_list, 0, len(date_list) - 1)


def _read_internal(needed_empty=False):
    global names_list, user_names_list, chat_ids_list, days_list, month_list
    excel_data = pandas.read_excel('res/leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()

    if needed_empty is False:
        empty_array = search.find_empty_leaders(days_list, month_list)
        for i in empty_array:
            names_list.remove(names_list[i])
            user_names_list.remove(user_names_list[i])
            chat_ids_list.remove(chat_ids_list[i])
            days_list.remove(days_list[i])
            month_list.remove(month_list[i])
    else:
        for i in range(len(days_list)):
            if math.isnan(days_list[i]):
                days_list[i] = 1
            if math.isnan(month_list[i]):
                month_list[i] = 1


def _save_changes_in_excel():
    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('res/leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()

