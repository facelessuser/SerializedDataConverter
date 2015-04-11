import sublime

__all__ = ['error_msg']


def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e is not None:
        print("Serialized Data Converter:")
        print(e)
