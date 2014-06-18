import sublime

__all__ = ['error_msg', "load_settings"]

PACKAGE_SETTINGS = "serialized_data_converter.sublime-settings"


def load_settings(value, default=None):
    if value:
        return sublime.load_settings(PACKAGE_SETTINGS).get(value, default)
    else:
        return sublime.load_settings(PACKAGE_SETTINGS)


def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e is not None:
        print("Serialized Data Converter:")
        print(e)
