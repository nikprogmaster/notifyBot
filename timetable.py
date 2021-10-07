import leader
import pandas


def read_timetable():
    leaders = []
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()
    print(names_list)

    for i in range(0, len(names_list)):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        leaders.append(l)
    return leaders


def update_schedule():
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()

    for i in range(0, len(names_list) - 1):
        l = leader.Leader(names_list[i], user_names_list[i], chat_ids_list[i], days_list[i], month_list[i])
        l.append_date(len(names_list))
        days_list[i] = l.date.day
        month_list[i] = l.date.month

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()


def update_first_leader():
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()
    length = len(names_list)
    l = leader.Leader(names_list[length - 1], user_names_list[length - 1], chat_ids_list[length - 1],
                      days_list[length - 1], month_list[length - 1])
    l.append_date(len(names_list))
    days_list[length - 1] = l.date.day
    month_list[length - 1] = l.date.month

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()


def delete_from_schedule(username, leaders):
    excel_data = pandas.read_excel('leading.xlsx', sheet_name='Timetable')
    names_list = excel_data['Name'].tolist()
    user_names_list = excel_data['User name'].tolist()
    chat_ids_list = excel_data['Chat id'].tolist()
    days_list = excel_data['Day'].tolist()
    month_list = excel_data['Month'].tolist()

    user_index = 0
    for i in user_names_list:
        if i == username:
            user_index = user_names_list.index(i)

    if user_index != 0:
        start_index = 0
        if leaders[0].date < leaders[len(leaders)-1].date:
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

    result_frame = pandas.DataFrame(
        {'Name': names_list,
         'User name': user_names_list,
         'Chat id': chat_ids_list,
         'Day': days_list,
         'Month': month_list})
    writer = pandas.ExcelWriter('leading.xlsx', engine='xlsxwriter')
    result_frame.to_excel(writer, 'Timetable', index=False)
    writer.save()


