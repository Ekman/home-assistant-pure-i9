"""Integration exceptions"""

class PureI9Exception(Exception):
    """Base exception for all integration exceptions"""
    def __init__(self, msg):
        self.msg = msg

class CommandException(PureI9Exception):
    """Exception indicating an error in a vacuum command"""
    def __init__(self, msg):
        super().__init__(msg)

class CommandParamException(PureI9Exception):
    """Exception indicating invalid vacuum command parameter"""
    def __init__(self, name, type):
        super().__init__(f"Need \"{name}\" of type \"{type}\".")
        self.name = name
        self.type = type
