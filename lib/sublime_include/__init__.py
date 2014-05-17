from __future__ import absolute_import
import sublime
import sys
from os import exists

__all__ = ["ST3", "ST2", "json", "plist", "yaml", "load_settings"]

ST3 = 3000 <= int(sublime.version()) < 4000
ST2 = 2000 <= int(sublime.version()) < 3000
PACKAGE_SETTINGS = "serialized_data_converter.sublime-settings"


def load_settings(value, default=None):
    if value:
        return sublime.load_settings(PACKAGE_SETTINGS).get(value, default)
    else:
        return sublime.load_settings(PACKAGE_SETTINGS)


# Load up python lib for ST2
if ST2 and sublime.platform() == "linux":
    # Try and load Linux Python2.6 lib.  Default path is for Ubuntu.
    linux_lib = load_settings().get("linux_python2.6_lib", "/usr/lib/python2.6/lib-dynload")
    if linux_lib not in sys.path and exists(linux_lib):
        sys.path.append(linux_lib)

if ST3:
    from .st3 import json
    from .st3 import plist
    from .st3 import yaml
else:
    from .st2 import json
    from .st2 import plist
    from .st2 import yaml
