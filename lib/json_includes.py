import sublime
import json
import plistlib
import base64
from .file_strip.json import sanitize_json

__all__ = ["readJsonFromView", "jsonDumps"]


jsonDumps = lambda obj, preserve_binary=False: json.dumps(
    json_convert_to(obj, preserve_binary), sort_keys=True, indent=4, separators=(',', ': ')
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
def json_convert_to(obj, preserve_binary=False):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = json_convert_to(v, preserve_binary)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_to(v, preserve_binary)
            count += 1
    elif isinstance(obj, plistlib.Data):
        if preserve_binary:
            obj = {"!!python/object:plistlib.Data": base64.b64encode(obj.data).decode("ascii")}
        else:
            obj = base64.b64encode(obj.data).decode("ascii")

    return obj


def json_convert_from(obj):
    if isinstance(obj, dict):
        if len(obj) == 1 and "!!python/object:plistlib.Data" in obj:
            try:
                obj = plistlib.Data(base64.decodebytes(obj["!!python/object:plistlib.Data"].encode('ascii')))
            except:
                obj = obj["!!python/object:plistlib.Data"]
        else:
            for k, v in obj.items():
                obj[k] = json_convert_from(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_from(v)
            count += 1

    return obj
