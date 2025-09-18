from datetime import datetime

def getNow():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')