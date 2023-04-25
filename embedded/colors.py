class TextColors:
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    LOG = '\033[90m'
    BLUE = '\033[94m'
    ENDCOLOR = '\033[0m'
    
def print_color(msg, color):
    if color == "error":
        print(TextColors.ERROR, end="")
    elif color == "log":
        print(TextColors.LOG, end="")
    elif color == "success":
        print(TextColors.SUCCESS, end="")
    elif color == "warning":
        print(TextColors.WARNING, end="")
    elif color == "blue":
        print(TextColors.BLUE, end="")
        
    print(msg)
    print(TextColors.ENDCOLOR, end="")