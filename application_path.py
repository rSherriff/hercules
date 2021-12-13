import sys,os

def get_app_path():
    if getattr(sys, 'frozen', False):
        #Will only work if frozen with pyinstaller
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))