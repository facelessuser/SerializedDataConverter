"""
Plist Json Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""
import re
from os.path import splitext
import traceback
from .lib.language_converter import LanguageConverter as _LanguageConverter
from .lib import json_includes as json
from .lib import plist_includes as plist
from .lib.common_include import *

ERRORS = {
    "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
    "plist2json": "Could not convert PLIST to JSON!\nPlease see console for more info.",
    "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
    "json2plist": "Could not convert JSON to PLIST!\nPlease see console for more info."
}


class SerializedPlistToJsonCommand(_LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = load_settings("plist_json_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["plist"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["json"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".JSON"
        return name

    def read_buffer(self):
        errors = False
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            self.plist = plist.readPlistFromView(self.view)
        except:
            errors = True
            error_msg(ERRORS["view2plist"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                self.output = json.jsonDumps(
                    self.plist,
                    preserve_binary=load_settings("json_preserve_binary_data", True)
                )
        except:
            errors = True
            error_msg(ERRORS["plist2json"], traceback.format_exc())
        return errors


class SerializedJsonToPlistCommand(_LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = load_settings("plist_json_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["json"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["plist"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".plist"
        return name

    def read_buffer(self):
        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.json = json.readJsonFromView(self.view)

        except:
            errors = True
            error_msg(ERRORS["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = plist.plistDumps(
                self.json,
                detect_timestamp=load_settings("plist_detect_timestamp", True),
                none_handler=load_settings("plist_none_handler", "fail")
            )
        except:
            errors = True
            error_msg(ERRORS["json2plist"], traceback.format_exc())
        return errors
