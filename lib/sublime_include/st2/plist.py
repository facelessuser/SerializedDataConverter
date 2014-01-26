import sublime
import plistlib
import StringIO
import datetime


__all__ = ["readPlistFromView", "plistDumps"]

plistDumps = lambda obj, detect_timestamp=False, none_handler="fail": plistlib.writePlistToString(
    plist_convert_to(obj, detect_timestamp, none_handler)
).decode('utf-8')


readPlistFromView = lambda view: plist_convert_from(
    plistlib.readPlist(
        StringIO.StringIO(
            view.substr(
                sublime.Region(0, view.size())
            ).encode('utf8')
        )
    )
)


def convert_timestamp(obj):
    time_stamp = None
    if plistlib._dateParser.match(obj):
        time_stamp = plistlib._dateFromString(obj)
    return time_stamp


def plist_convert_from(obj):
    if isinstance(obj, plistlib._InternalDict):
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
    elif isinstance(obj, basestring) and detect_timestamp:
        time_stamp = convert_timestamp(obj)
        if time_stamp is not None:
            obj = time_stamp

    return obj