import sublime

__all__ = ['PACKAGE_SETTINGS', 'error_msg']

PACKAGE_SETTINGS = "serialized_data_converter.sublime-settings"


def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e is not None:
        print("Serialized Data Converter:")
        print(e)
