from __future__ import absolute_import
import sublime
from .file_strip.json import sanitize_json
import json
from .common_include import *

if ST3 and sublime.platform() == "linux":
    # Try and load Linux Python2.6 lib.  Default path is for Ubuntu.
    linux_lib = sublime.load_settings(PACKAGE_SETTINGS).get("linux_python2.6_lib", "/usr/lib/python2.6/lib-dynload")
    if not linux_lib in sys.path and exists(linux_lib):
        sys.path.append(linux_lib)

import plistlib

__all__ = ['plistlib', 'json', 'sanitize_json']
