import sublime
from .sublime_include import load_settings, ST3, ST2

__all__ = ['error_msg', "load_settings", "ST3", "ST2"]

def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e is not None:
        print("Serialized Data Converter:")
        print(e)
