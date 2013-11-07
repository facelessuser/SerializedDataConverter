"""
Plist Json Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import sublime
import sublime_plugin
import json
import re
from os.path import splitext
from SerializedDataConverter.lib.language_converter import LanguageConverter as _LanguageConverter
from SerializedDataConverter.lib.language_converter import LanguageListener as _LanguageListener
from SerializedDataConverter.lib.common_include import error_msg, PACKAGE_SETTINGS
from SerializedDataConverter.lib.json_includes import *
import traceback


ERRORS = {
    "plist2json": "Could not convert PLIST to JSON!\nPlease see console for more info.",
    "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
    "json2plist": "Could not convert JSON to PLIST!\nPlease see console for more info."
}


class SerializedDataJsonListener(_LanguageListener):
    def get_save_ext(self):
        return sublime.load_settings(PACKAGE_SETTINGS).get("json_to_plist_on_save", [])

    def convert(self, view):
        view.run_command("json_to_plist", {"save_to_file": 'True', "show_file": False, "force": True})


class PlistToJsonCommand(_LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/Javascript/JSON.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("plist_json_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["plist"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["other"]
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
            self.plist = plistlib.readPlistFromBytes(
                self.view.substr(
                    sublime.Region(0, self.view.size())
                ).encode('utf8')
            )
        except:
            errors = True
            error_msg(ERRORS["view2plist"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                self.output = json.dumps(self.plist, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8').decode('raw_unicode_escape')
        except:
            errors = True
            error_msg(ERRORS["plist2json"], traceback.format_exc())
        return errors


class JsonToPlistCommand(_LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("plist_json_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["other"]) + "$", filename, re.IGNORECASE)
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
            self.json = json.loads(
                sanitize_json(
                    self.view.substr(
                        sublime.Region(0, self.view.size())
                    ),
                    True
                )
            )

        except:
            errors = True
            error_msg(ERRORS["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = plistlib.writePlistToBytes(self.json).decode('utf-8')
        except:
            errors = True
            error_msg(ERRORS["json2plist"], traceback.format_exc())
        return errors
