"""
Plist/Yaml Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import sublime
import re
from os.path import splitext
from SerializedDataConverter.lib.language_converter import LanguageConverter as _LanguageConverter
from SerializedDataConverter.lib.language_converter import LanguageListener as _LanguageListener
from SerializedDataConverter.lib.common_include import error_msg, PACKAGE_SETTINGS
from SerializedDataConverter.lib.yaml_includes import *
import traceback


ERRORS = {
    "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
    "plist2yaml": "Could not convert PLIST to YAML!\nPlease see console for more info.",
    "view2yaml": "Could not read view buffer as YAML!\nPlease see console for more info.",
    "yaml2plist": "Could not convert YAML to PLIST!\nPlease see console for more info."
}


class SerializedDataYamlListener(_LanguageListener):
    def get_save_ext(self):
        return sublime.load_settings(PACKAGE_SETTINGS).get("yaml_to_plist_on_save", [])

    def convert(self, view):
        view.run_command("yaml_to_plist", {"save_to_file": 'True', "show_file": False, "force": True})


class PlistToYamlCommand(_LanguageConverter):
    lang = "yaml_language"
    default_lang = "Packages/SerializedDataConverter/languages/YAML.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("plist_yaml_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["plist"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["other"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".YAML"
        return name

    def yaml_strip(self, obj):
        if isinstance(obj, (dict, plistlib._InternalDict)):
            for k, v in obj.items():
                obj[k] = self.yaml_strip(v)
        elif isinstance(obj, list):
            count = 0
            for v in obj:
                obj[count] = self.yaml_strip(v)
                count += 1
        elif self.strip_tabs and isinstance(obj, str):
            obj = obj.replace("\t", "    ").rstrip(" ")

        return obj

    def read_buffer(self):
        errors = False
        ext_tbl = sublime.load_settings(self.settings).get("yaml_strip_tabs_from", [])
        filename = self.view.file_name()
        self.strip_tabs = False
        if filename is not None:
            for ext in ext_tbl:
                m = re.match("^(.*)\\." + re.escape(ext) + "$", filename, re.IGNORECASE)
                if m is not None:
                    self.strip_tabs = True
                    break
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            self.plist = plistlib.readPlistFromBytes(
                self.view.substr(
                    sublime.Region(0, self.view.size())
                ).encode('utf8')
            )
            if self.strip_tabs:
                self.plist = self.yaml_strip(self.plist)
        except:
            errors = True
            error_msg(ERRORS["view2plist"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                self.output = yaml.dump(
                    self.plist,
                    width=None,
                    indent=4,
                    allow_unicode=True,
                    default_flow_style=not bool(sublime.load_settings(self.settings).get("yaml_no_inline", False))
                )
        except:
            errors = True
            error_msg(ERRORS["plist2yaml"], traceback.format_exc())
        return errors


class YamlToPlistCommand(_LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("plist_yaml_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["other"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["plist"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".yaml"
        return name

    def read_buffer(self):
        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.yaml = yaml.load(
                self.view.substr(
                    sublime.Region(0, self.view.size())
                )
            )

        except:
            errors = True
            error_msg(ERRORS["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = plistlib.writePlistToBytes(self.yaml).decode('utf-8')
        except:
            errors = True
            error_msg(ERRORS["yaml2plist"], traceback.format_exc())
        return errors
