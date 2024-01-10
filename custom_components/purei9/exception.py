"""Integration exceptions"""

class PureI9Exception(Exception):
    """Base exception for all integration exceptions"""

class CommandException(PureI9Exception):
    """Exception indicating an error in a vacuum command"""

class CommandParamException(PureI9Exception):
    """Exception indicating invalid vacuum command parameter"""
    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.type = type
