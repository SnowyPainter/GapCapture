import datetime
class Logger:
    def log(self, text):
        now = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        with open(self.fname, "a") as myfile:
            myfile.write(f"[{now}]\t{text}\n")
    def __init__(self, title) -> None:
        self.fname = datetime.datetime.now().strftime("%Y %m %d") + ".txt"
        self.log(title)