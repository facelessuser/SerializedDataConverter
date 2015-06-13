"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import sublime

__all__ = ('error_msg',)


def error_msg(msg, e=None):
    """Error message."""

    sublime.error_message(msg)
    if e is not None:
        print("Serialized Data Converter:")
        print(e)
