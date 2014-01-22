"""
JSON/Yaml Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import sublime
import re
import json
from os.path import splitext
import traceback
if int(sublime.version()) >= 3000:
    from .lib.language_converter import LanguageConverter as _LanguageConverter
    from .lib.json_includes import *
    from .lib.yaml_includes import *
else:
    from lib.language_converter import LanguageConverter as _LanguageConverter
    from lib.json_includes import *
    from lib.yaml_includes import *

ERRORS = {
    "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
    "yaml2json": "Could not convert YAML to JSON!\nPlease see console for more info.",
    "view2yaml": "Could not read view buffer as YAML!\nPlease see console for more info.",
    "json2yaml": "Could not convert JSON to YAML!\nPlease see console for more info."
}

class SerializedJsonToYamlCommand(_LanguageConverter):
    lang = "yaml_language"
    default_lang = "Packages/YAML/YAML.tmLanguage"

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = load_settings("json_yaml_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["json"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["yaml"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".YAML"
        return name

    def read_buffer(self):
        errors = False
        ext_tbl = load_settings("yaml_strip_tabs_from", [])
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
            self.json = json.readJsonFromView(self.view)
        except:
            errors = True
            error_msg(ERRORS["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                default_flow_style = None
                flow_setting = load_settings("yaml_default_flow_style", None)
                if flow_setting == "true":
                    default_flow_style = True
                elif flow_setting == "false":
                    default_flow_style = False

                self.output = yaml.yamlDumps(self.json, default_flow_style=default_flow_style, strip_tabs=self.strip_tabs)
        except:
            errors = True
            error_msg(ERRORS["json2yaml"], traceback.format_exc())
        return errors

class SerializedYamlToJsonCommand(_LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = load_settings("json_yaml_conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + re.escape(ext["yaml"]) + "$", filename, re.IGNORECASE)
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
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.yaml = yaml.readYamlFromView(self.view)
        except:
            errors = True
            error_msg(ERRORS["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = json.jsonDumps(self.yaml)
        except:
            errors = True
            error_msg(ERRORS["yaml2json"], traceback.format_exc())
        return errors
