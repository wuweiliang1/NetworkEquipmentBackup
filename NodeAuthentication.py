class NodeAuthentication:
    """
    handle authentication information in this class. Initialized by node type

    """
    def __init__(self, nodetype):
        """
        :type nodetype: string name of node type, such as ciscoSwitch, h3c_switch, and so on
        """
        if nodetype == 'alteon':
            self._user = None
            self._password = 'xxxxxxx'
        elif nodetype == '3dns':
            self._user = 'admin'
            self._password = 'xxxxxxx'
        else:
            self._user = 'monitor'
            self._password = 'xxxxxxx'

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password
