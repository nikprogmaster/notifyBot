
class SuperuserSettings:

    def __init__(self):
        self.is_adding_user = False
        self.is_deleting_user = False
        self.is_temporarily_deleting = False
        self.is_changing_date = False
        self.is_transfering_rights = False
        self.is_swaping = False
        self.changing_date_leader = None
        self.swaping_leaders = []

    def set_states(self, is_deleting=False, is_adding=False, is_temporarily_deleting=False, is_changing_date=False,
                   is_swaping=False, is_transfering_rights=False):
        self.is_deleting_user = is_deleting
        self.is_adding_user = is_adding
        self.is_temporarily_deleting = is_temporarily_deleting
        self.is_changing_date = is_changing_date
        self.is_swaping = is_swaping
        self.is_transfering_rights = is_transfering_rights

