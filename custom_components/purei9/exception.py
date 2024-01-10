class PureI9Exception(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg

class CommandException(PureI9Exception):
    """asd"""

class CommandParamException(PureI9Exception):
    def __init__(self, name, type):
        self.msg = f"Need \"{name}\" of type \"{type}\"."
        self.name = name
        self.type = type
