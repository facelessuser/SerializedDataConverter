import sublime
import sublime_plugin
import codecs
import re
import traceback
from os.path import exists, basename, splitext
from SerializedDataConverter.lib.log import error_msg
from SerializedDataConverter.lib import plist_includes as plist
from SerializedDataConverter.lib import yaml_includes as yaml
from SerializedDataConverter.lib import json_includes as json

PACKAGE_SETTINGS = "serialized_data_converter.sublime-settings"


class SerializedDataConverterListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        ext2convert = self.get_save_ext()
        filename = view.file_name()
        command = None
        if filename is not None:
            for converter in ext2convert:
                ext = converter.get("ext", None)
                if ext is not None and filename.lower().endswith(ext.lower()):
                    command = converter.get("command", None)
                    break

        if command is not None:
            self.convert(view, command)

    def get_save_ext(self):
        return sublime.load_settings(PACKAGE_SETTINGS).get("convert_on_save", [])

    def convert(self, view, command):
        view.run_command("serialized_%s" % command, {"save_to_file": 'True', "show_file": False, "force": True})


class LanguageConverter(object):
    lang = None
    default_lang = "Packages/Text/Plain text.tmLanguage"
    errors = {
        "filewrite": "Could not write file!\nPlease see console for more info.",
        "bufferwrite": "Could not write view buffer!\nPlease see console for more info.",
        "yaml2json": "Could not convert YAML to JSON!\nPlease see console for more info.",
        "view2yaml": "Could not read view buffer as YAML!\nPlease see console for more info.",
        "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
        "json2yaml": "Could not convert JSON to YAML!\nPlease see console for more info.",
        "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
        "plist2yaml": "Could not convert PLIST to YAML!\nPlease see console for more info.",
        "view2yaml": "Could not read view buffer as YAML!\nPlease see console for more info.",
        "yaml2plist": "Could not convert YAML to PLIST!\nPlease see console for more info.",
        "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
        "json2plist": "Could not convert JSON to PLIST!\nPlease see console for more info.",
        "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
        "plist2json": "Could not convert PLIST to JSON!\nPlease see console for more info."
    }

    def setup(self):
        self.settings = sublime.load_settings(PACKAGE_SETTINGS)

    def set_syntax(self):
        if self.output_view is not None:
            # Get syntax language and set it
            syntax = self.settings.get(self.lang, self.default_lang) if self.lang is not None else self.default_lang
            self.output_view.set_syntax_file(syntax)

    def write_file(self, edit, show_file):
        errors = False
        # Get current view's filename
        filename = self.view.file_name()
        save_filename = self.get_output_file(filename) if filename is not None and exists(filename) else None

        if save_filename is not None:
            # Save content to UTF file
            try:
                if self.save_binary:
                    with open(save_filename, "wb") as f:
                        f.write(self.output)
                else:
                    with codecs.open(save_filename, "w", "utf-8") as f:
                        f.write(self.output)
                self.output = None
                if show_file:
                    self.output_view = self.view.window().open_file(save_filename)
            except:
                errors = True
                error_msg(self.errors["filewrite"], traceback.format_exc())
            if not errors and show_file:
                self.set_syntax()
        else:
            # Could not acquire a name that exists on disk
            # Fallback to buffer write
            self.write_buffer(edit, force_new_buffer=True)

    def write_buffer(self, edit, force_new_buffer=False):
        errors = False
        new_buffer = bool(self.settings.get("open_in_new_buffer", False))

        # Save content to view buffer
        try:
            self.output_view = self.view.window().new_file() if new_buffer or force_new_buffer else self.view
            self.output_view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                self.output
            )
            self.output = None
        except:
            errors = True
            error_msg(self.errors["bufferwrite"], traceback.format_exc())

        if not errors:
            if new_buffer or force_new_buffer:
                # If a name can be acquired from the original view, give buffer a modified derivative of the name
                filename = self.view.file_name()
                buffer_name = basename(self.get_output_file(filename)) if filename is not None else None
                if buffer_name is not None:
                    self.output_view.set_name(buffer_name)
            self.set_syntax()

    def _is_enabled(self, **kwargs):
        enabled = True
        filename = self.view.file_name()
        view_okay = True
        if kwargs.get('binary', False) and (filename is None or not exists(filename)):
            view_okay = False

        if not kwargs.get('force', False):
            if (
                kwargs.get('save_to_file', False) and
                not bool(self.settings.get("enable_save_to_file_commands", False))
            ):
                enabled = False
            elif (
                not kwargs.get('save_to_file', False) and
                not bool(self.settings.get("enable_show_in_buffer_commands", False))
            ):
                enabled = False
        if not view_okay and enabled:
            enabled = False
        return enabled

    def get_output_file(self, filename):
        return self.view

    def read_buffer(self):
        return False

    def convert(self, edit):
        return False

    def _run(self, edit, **kwargs):
        self.binary = kwargs.get('binary', False)
        self.save_binary = kwargs.get('save_binary', False)
        if not self.read_buffer():
            if not self.convert(edit):
                if kwargs.get('save_to_file', False):
                    self.write_file(edit, kwargs.get('show_file', True))
                else:
                    self.write_buffer(edit)


##########################
# Plist <-> YAML
##########################
class SerializedPlistToYamlCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "yaml_language"
    default_lang = "Packages/YAML/YAML.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("plist_yaml_conversion_ext", []):
            m = re.match("^(.*)\\." + re.escape(ext["plist"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["yaml"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".YAML"
        return name

    def read_buffer(self):
        errors = False
        ext_tbl = self.settings.get("yaml_strip_tabs_from", [])
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
            if self.binary and filename is not None and exists(filename):
                self.plist = plist.readPlistFromFile(filename)
            else:
                self.plist = plist.readPlistFromView(self.view)
        except:
            errors = True
            error_msg(self.errors["view2plist"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                default_flow_style = None
                flow_setting = self.settings.get("yaml_default_flow_style", None)
                if flow_setting == "true":
                    default_flow_style = True
                elif flow_setting == "false":
                    default_flow_style = False

                # Convert Python dict to Yaml buffer.
                self.output = yaml.yamlDumps(
                    self.plist,
                    default_flow_style=default_flow_style,
                    strip_tabs=self.strip_tabs,
                    detect_timestamp=self.settings.get("yaml_detect_timestamp", True)
                )
                self.plist = None
        except:
            errors = True
            error_msg(self.errors["plist2yaml"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)


class SerializedYamlToPlistCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("plist_yaml_conversion_ext", []):
            m = re.match("^(.*)\\." + re.escape(ext["yaml"]) + "$", filename, re.IGNORECASE)
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
            self.yaml = yaml.readYamlFromView(self.view)
        except:
            errors = True
            error_msg(self.errors["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            if self.save_binary:
                self.output = plist.plistBinaryDumps(
                    self.yaml,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            else:
                self.output = plist.plistDumps(
                    self.yaml,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            self.yaml = None
        except:
            errors = True
            error_msg(self.errors["yaml2plist"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)


##########################
# Plist <-> JSON
##########################
class SerializedPlistToJsonCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("plist_json_conversion_ext", []):
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
            filename = self.view.file_name()
            if self.binary and filename is not None and exists(filename):
                self.plist = plist.readPlistFromFile(filename)
            else:
                self.plist = plist.readPlistFromView(self.view)
        except:
            errors = True
            error_msg(self.errors["view2plist"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                self.output = json.jsonDumps(
                    self.plist,
                    preserve_binary=self.settings.get("json_preserve_binary_data", True)
                )
                self.plist = None
        except:
            errors = True
            error_msg(self.errors["plist2json"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)


class SerializedJsonToPlistCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("plist_json_conversion_ext", []):
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
            error_msg(self.errors["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            if self.save_binary:
                self.output = plist.plistBinaryDumps(
                    self.json,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            else:
                self.output = plist.plistDumps(
                    self.json,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            self.json = None
        except:
            errors = True
            error_msg(self.errors["json2plist"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)


##########################
# YAML <-> JSON
##########################
class SerializedJsonToYamlCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "yaml_language"
    default_lang = "Packages/YAML/YAML.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("json_yaml_conversion_ext", []):
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
        ext_tbl = self.settings.get("yaml_strip_tabs_from", [])
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
            error_msg(self.errors["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                default_flow_style = None
                flow_setting = self.settings.get("yaml_default_flow_style", None)
                if flow_setting == "true":
                    default_flow_style = True
                elif flow_setting == "false":
                    default_flow_style = False

                self.output = yaml.yamlDumps(
                    self.json,
                    default_flow_style=default_flow_style,
                    strip_tabs=self.strip_tabs,
                    detect_timestamp=self.settings.get("yaml_detect_timestamp", True)
                )
                self.json = None
        except:
            errors = True
            error_msg(self.errors["json2yaml"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)


class SerializedYamlToJsonCommand(sublime_plugin.TextCommand, LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        for ext in self.settings.get("json_yaml_conversion_ext", []):
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
            error_msg(self.errors["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = json.jsonDumps(
                self.yaml,
                preserve_binary=self.settings.get("json_preserve_binary_data", True)
            )
            self.yaml = None
        except:
            errors = True
            error_msg(self.errors["yaml2json"], traceback.format_exc())
        return errors

    def is_enabled(self, **kwargs):
        return self._is_enabled(**kwargs)

    def run(self, edit, **kwargs):
        self._run(edit, **kwargs)
