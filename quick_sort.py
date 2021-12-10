class QuickSort:

    def __init__(self, names_list, user_names_list, chat_ids_list, days_list, month_list):
        self.names_list = names_list
        self.user_names_list = user_names_list
        self.chat_ids_list = chat_ids_list
        self.days_list = days_list
        self.month_list = month_list

    def swap(self, i1, i2, values):
        s = values[i1]
        values[i1] = values[i2]
        values[i2] = s

        s = self.days_list[i1]
        self.days_list[i1] = self.days_list[i2]
        self.days_list[i2] = s

        s = self.month_list[i1]
        self.month_list[i1] = self.month_list[i2]
        self.month_list[i2] = s

        s = self.names_list[i1]
        self.names_list[i1] = self.names_list[i2]
        self.names_list[i2] = s

        s = self.user_names_list[i1]
        self.user_names_list[i1] = self.user_names_list[i2]
        self.user_names_list[i2] = s

        s = self.chat_ids_list[i1]
        self.chat_ids_list[i1] = self.chat_ids_list[i2]
        self.chat_ids_list[i2] = s

    def partition(self, values, l, r):
        x = values[r]
        less = l

        for i in range(l, r):
            if values[i] <= x:
                self.swap(i, less, values)
                less += 1
        self.swap(less, r, values)
        return less

    def quick_sort(self, values, l, r):
        if l < r:
            q = self.partition(values, l, r)
            self.quick_sort(values, l, q - 1)
            self.quick_sort(values, q + 1, r)
