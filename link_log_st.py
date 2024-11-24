class LinkStatus:
    """
        Current css status of navbar links
        __init__ - make all links grey
        'active' - make link brown (activated)
        Example of using:
            link_st.__init__()
            link_st.products = 'active'
    """

    def __init__(self):
        self.home = ''
        self.products = ''
        self.about = ''
        self.log_in = ''
        self.sign_up = ''
        self.profile_info = ''
        self.cart = ''
        self.log_out = ''
link_st = LinkStatus()


class LoggedStatus:
    """
        Class to remember logged user during the work of the project
        log_in - login user with email attribut
        log_out - logout user, email attribute is empty
    """
    def __init__(self):
        self.is_logged_in = False
        self.email = ''

    def log_in(self, email):
        self.is_logged_in = True
        self.email = email

    def log_out(self):
        self.is_logged_in = False
        self.email = ''
log_st = LoggedStatus()
