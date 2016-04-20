"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import sublime
from . import plistlib
import datetime
import re
import collections

__all__ = ("read_plist_from_view", "read_plist_from_file", "plist_dumps", "plist_binary_dumps")


def strip_plist_comments(text):
    """Strip comments from plist."""

    return re.sub(
        br"^[\r\n\s]*<!--[\s\S]*?-->[\s\r\n]*|<!--[\s\S]*?-->", b'',
        text
    )


def convert_from_hex(view):
    """Convert Sublime hex view to bytes."""

    text = view.substr(sublime.Region(0, view.size())).replace(' ', '').replace('\n', '')
    byte = []
    offset = 0
    for x in range(0, int(len(text) / 2)):
        byte.append(int(text[x + offset:x + offset + 2], 16))
        offset += 1
    return bytes(byte)


def plist_dumps(obj, detect_timestamp=False, none_handler="fail"):
    """Wrapper for PLIST dump."""

    return plistlib.writePlistToBytes(
        plist_convert_to(obj, detect_timestamp, none_handler)
    ).decode('utf-8')


def plist_binary_dumps(obj, detect_timestamp=False, none_handler="fail"):
    """Wrapper for PLIST binary dump."""

    return plistlib.dumps(
        plist_convert_to(obj, detect_timestamp, none_handler),
        fmt=plistlib.FMT_BINARY
    )


def read_plist_from_hex_view(view):
    """Read PLIST from a Sublime hex view."""

    return plist_convert_from(
        plistlib.readPlistFromBytes(
            strip_plist_comments(convert_from_hex(view))
        )
    )


def read_plist_from_view(view):
    """Read PLIST from  a Sublime view."""

    return plist_convert_from(
        plistlib.readPlistFromBytes(
            strip_plist_comments(
                view.substr(
                    sublime.Region(0, view.size())
                ).encode('utf8')
            )
        )
    )


def read_plist_from_file(filename):
    """
    Read PLIST from filename.

    This is only used when reading binary plists,
    so no need to strip comments.
    """

    return plist_convert_from(
        plistlib.readPlist(filename)
    )


def convert_timestamp(obj):
    """Convert plist timestamp."""

    time_stamp = None
    if plistlib._dateParser.match(obj):
        time_stamp = plistlib._dateFromString(obj)
    return time_stamp


def sorted_dict(obj):
    """Sort dict."""

    return collections.OrderedDict(sorted(obj.items()))


def plist_convert_from(obj):
    """Convert specific plist items to a form usable by others."""

    if isinstance(obj, plistlib._InternalDict):
        obj = sorted_dict(obj)
        for k, v in obj.items():
            obj[k] = plist_convert_from(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = plist_convert_from(v)
            count += 1
    elif isinstance(obj, datetime.datetime):
        obj = plistlib._dateToString(obj)

    return obj


def plist_convert_to(obj, detect_timestamp=False, none_handler="fail"):
    """Convert specific serialized items to a plist format."""

    if isinstance(obj, dict):
        for k, v in (list(obj.items()) if none_handler == "strip" else obj.items()):
            if none_handler == "strip" and v is None:
                del obj[k]
            elif none_handler == "false" and v is None:
                obj[k] = False
            else:
                obj[k] = plist_convert_to(v, detect_timestamp, none_handler)
    elif isinstance(obj, list):
        count = 0
        offset = 0
        for v in (obj[:] if none_handler == "strip" else obj):
            if none_handler == "strip" and v is None:
                del obj[count - offset]
                offset += 1
            elif none_handler == "false" and v is None:
                obj[count - offset] = False
            else:
                obj[count - offset] = plist_convert_to(v, detect_timestamp, none_handler)
            count += 1
    elif isinstance(obj, str) and detect_timestamp:
        time_stamp = convert_timestamp(obj)
        if time_stamp is not None:
            obj = time_stamp

    return obj
