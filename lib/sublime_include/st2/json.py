from __future__ import absolute_import
import sublime
import json
from ...file_strip.json import sanitize_json

__all__ = ["readJsonFromView", "jsonDumps"]

jsonDumps = lambda obj: json.dumps(
    obj, sort_keys=True, indent=4, separators=(',', ': ')
).decode('raw_unicode_escape')

readJsonFromView = lambda view: json.loads(
    sanitize_json(
        view.substr(
            sublime.Region(0, view.size())
        ),
        True
    )
)
