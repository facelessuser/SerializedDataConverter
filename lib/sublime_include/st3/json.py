from __future__ import absolute_import
import sublime
import json
import plistlib
import datetime
from ...file_strip.json import sanitize_json
import base64

__all__ = ["readJsonFromView", "jsonDumps"]

jsonDumps = lambda obj: json.dumps(
    json_convert_to(obj), sort_keys=True, indent=4, separators=(',', ': ')
).encode('utf-8').decode('raw_unicode_escape')

readJsonFromView = lambda view: json_convert_from(
    json.loads(
        sanitize_json(
            view.substr(
                sublime.Region(0, view.size())
            ),
            True
        )
    )
)

# Strip tabs and trailing spaces to allow block format to successfully be triggered
def json_convert_to(obj):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = json_convert_to(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_to(v)
            count += 1
    elif isinstance(obj, plistlib.Data):
        return {"python/object:plistlib.Data": base64.b64encode(obj.data).decode("ascii")}
    elif isinstance(obj, datetime.datetime):
        return plistlib._dateToString(obj)

    return obj


def json_convert_from(obj):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        if len(obj) == 1 and "python/object:plistlib.Data" in obj:
            obj = plistlib.Data(obj["python/object:plistlib.Data"].encode('ascii'))
        else:
            for k, v in obj.items():
                obj[k] = json_convert_from(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_from(v)
            count += 1
    elif isinstance(obj, str) and plistlib._dateParser.match(obj):
        return plistlib._dateFromString(obj)

    return obj
