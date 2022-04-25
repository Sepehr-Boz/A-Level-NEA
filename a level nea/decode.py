import os

class Decode():
    def __init__(self, code):
        self.code = code + "\n"

    def GetOutput(self):
        file = open("python_file.py", "w")
        file.write(self.code)
        file.close()

        try:
            result = os.popen("python_file.py").read()
        except:
            result = ""

        os.remove("python_file.py")

        return result