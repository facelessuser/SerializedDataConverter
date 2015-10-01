"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
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


def to_hex(value):
    """Convert int value to hex string."""

    return "%02x" % value


class SerializedDataConverterListener(sublime_plugin.EventListener):

    """Listener to convert certain files on save."""

    def on_post_save(self, view):
        """Convert after saves."""

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
        """Get the save extension."""

        return sublime.load_settings(PACKAGE_SETTINGS).get("convert_on_save", [])

    def convert(self, view, command):
        """Call the appropriate convert command."""

        binary = False
        save_binary = False
        if command.startswith('bplist'):
            command = command.replace('bplist', 'plist')
            binary = True
        elif command.endswith('bplist'):
            command = command.replace('bplist', 'plist')
            save_binary = True

        view.run_command(
            "serialized_%s" % command, {
                "save_to_file": 'True',
                "show_file": False,
                "force": True,
                "binary": binary,
                'save_binary': save_binary
            }
        )


class _LanguageConverter(sublime_plugin.TextCommand):

    """Language converter base class."""

    lang = None
    default_lang = "Packages/Text/Plain text.tmLanguage"
    errors = {
        "filewrite": "Could not write file!\n"
                     "Please see console for more info.",
        "bufferwrite": "Could not write view buffer!\n"
                       "Please see console for more info.",
        "view2yaml": "Could not read view buffer as YAML!\n"
                     "Please see console for more info.",
        "view2json": "Could not read view buffer as JSON!\n"
                     "Please see console for more info.",
        "view2plist": "Could not read view buffer as PLIST!\n"
                      "Please see console for more info.",
        "view2bplist": "Could not read view buffer as Binary PLIST!\n"
                       "Please see console for more info.",
        "yaml2json": "Could not convert YAML to JSON!\n"
                     "Please see console for more info.",
        "json2yaml": "Could not convert JSON to YAML!\n"
                     "Please see console for more info.",
        "plist2yaml": "Could not convert PLIST to YAML!\n"
                       "Please see console for more info.",
        "bplist2yaml": "Could not convert Binary PLIST to YAML!\n"
                       "Please see console for more info.",
        "yaml2plist": "Could not convert YAML to PLIST!\n"
                       "Please see console for more info.",
        "yaml2bplist": "Could not convert YAML to Binary PLIST!\n"
                       "Please see console for more info.",
        "json2plist": "Could not convert JSON to PLIST!\n"
                       "Please see console for more info.",
        "json2bplist": "Could not convert JSON to Binary PLIST!\n"
                       "Please see console for more info.",
        "plist2json": "Could not convert PLIST to JSON!\n"
                       "Please see console for more info.",
        "bplist2json": "Could not convert Binary PLIST to JSON!\n"
                       "Please see console for more info.",
        "bplist2plist": "Could not convert Binary PLIST to PLIST!\n"
                       "Please see console for more info.",
        "plist2bplist": "Could not convert PLIST to Binary PLIST!\n"
                       "Please see console for more info.",
        "binwrite": "Source view does not exist on disk, so save name and location cannot be determined.\n"
                    "You can convert and save to disk as an XML PLIST and then convert it to BPLIST."
    }

    def __init__(self, *args, **kwargs):
        """General setup."""

        self.settings = sublime.load_settings(PACKAGE_SETTINGS)
        super().__init__(*args, **kwargs)

    def set_syntax(self):
        """Set the view syntax."""

        if self.output_view is not None:
            # Get syntax language and set it
            self.output_view.set_syntax_file(self.syntax)

    def write_file(self, edit, show_file):
        """Write data to a file if a location can be acquired else save to a view buffer."""

        errors = False

        if self.save_filename is not None and exists(self.save_filename):
            # Save content to UTF file
            try:
                if self.save_binary:
                    with open(self.save_filename, "wb") as f:
                        f.write(self.output)
                else:
                    with codecs.open(self.save_filename, "w", "utf-8") as f:
                        f.write(self.output)
                self.output = None
                if show_file:
                    self.output_view = self.view.window().open_file(self.save_filename)
            except Exception:
                errors = True
                error_msg(self.errors["filewrite"], traceback.format_exc())
            if not errors and show_file:
                self.set_syntax()
        else:
            # Could not acquire a name that exists on disk
            # Fallback to buffer write
            self.write_buffer(edit, force_new_buffer=True)

    def write_buffer(self, edit, force_new_buffer=False):
        """Write the data to a view buffer."""

        errors = False
        new_buffer = bool(self.settings.get("open_in_new_buffer", False))

        # Save content to view buffer
        try:
            self.output_view = self.view.window().new_file() if new_buffer or force_new_buffer else self.view
            if self.save_binary:
                self.output_view.set_encoding('Hexadecimal')
                bin_output = []
                count = 0
                for b in self.output:
                    if count % 16 == 0 and count != 0:
                        bin_output += ['\n', to_hex(b)]
                    else:
                        if count % 2 == 0 and count != 0:
                            bin_output += [' ', to_hex(b)]
                        else:
                            bin_output.append(to_hex(b))
                    count += 1
                self.output = None
                self.output_view.replace(
                    edit,
                    sublime.Region(0, self.view.size()),
                    ''.join(bin_output)
                )
                bin_output = None
            else:
                self.output_view.set_encoding('UTF-8')
                print(self.output)
                self.output_view.replace(
                    edit,
                    sublime.Region(0, self.view.size()),
                    self.output
                )
                self.output = None
        except Exception:
            errors = True
            error_msg(self.errors["bufferwrite"], traceback.format_exc())

        if not errors:
            if new_buffer or force_new_buffer:
                # If a name can be acquired from the original view,
                # give buffer a modified derivative of the name.
                if self.save_filename is not None:
                    self.output_view.set_name(basename(self.save_filename))
            self.set_syntax()

    def is_enabled(self, **kwargs):
        """Determine if the command should be enabled."""

        enabled = True
        filename = self.view.file_name()
        view_okay = True
        if (
            kwargs.get('binary', False) and
            (filename is None or not exists(filename)) and
            self.view.encoding() != 'Hexadecimal'
        ):
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
        """Get output filename to save to."""

        return None

    def read_source(self):
        """Read the source."""

        return False

    def convert(self, edit):
        """Convert the read data to the desired format."""

        return False

    def run(self, edit, **kwargs):
        """Begin conversion."""

        self.binary = kwargs.get('binary', False)
        self.save_binary = kwargs.get('save_binary', False)
        self.syntax = self.settings.get(self.lang, self.default_lang) if self.lang is not None else self.default_lang
        filename = self.view.file_name()
        self.save_filename = self.get_output_file(filename) if filename is not None else None
        if not self.read_source():
            if not self.convert(edit):
                if kwargs.get('save_to_file', False):
                    self.write_file(edit, kwargs.get('show_file', True))
                else:
                    self.write_buffer(edit)


##########################
# Plist <-> YAML
##########################
class SerializedPlistToYamlCommand(_LanguageConverter):

    """Convert PLIST to YAML."""

    lang = "yaml_language"
    default_lang = "Packages/YAML/YAML.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""

        name = None

        if self.binary:
            setting = 'bplist_yaml_conversion_ext'
            src = 'bplist'
        else:
            setting = 'plist_yaml_conversion_ext'
            src = 'plist'

        # Try and find file ext in the ext table
        for ext in self.settings.get(setting, []):
            m = re.match("^(.*)\\." + re.escape(ext[src]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["yaml"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".YAML"
        return name

    def read_source(self):
        """Read the source."""

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
            if self.binary and self.view.encoding() == 'Hexadecimal':
                self.plist = plist.read_plist_from_hex_view(self.view)
            elif self.binary and filename is not None and exists(filename):
                self.plist = plist.read_plist_from_file(filename)
            else:
                self.plist = plist.read_plist_from_view(self.view)
        except Exception:
            errors = True
            error_type = 'view2bplist' if self.binary else 'view2plist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

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
                self.output = yaml.yaml_dumps(
                    self.plist,
                    default_flow_style=default_flow_style,
                    indent=self.settings.get("yaml_indent"),
                    strip_tabs=self.strip_tabs,
                    detect_timestamp=self.settings.get("yaml_detect_timestamp", True)
                )
                self.plist = None
        except Exception:
            errors = True
            error_type = 'bplist2yaml' if self.binary else 'plist2yaml'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors


class SerializedYamlToPlistCommand(_LanguageConverter):

    """Convert YAML to PLIST."""

    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""

        name = None

        if self.save_binary:
            setting = 'bplist_yaml_conversion_ext'
            out = 'bplist'
        else:
            setting = 'plist_yaml_conversion_ext'
            out = 'plist'

        # Try and find file ext in the ext table
        for ext in self.settings.get(setting, []):
            m = re.match("^(.*)\\." + re.escape(ext["yaml"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext[out]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".plist"
        return name

    def read_source(self):
        """Read the source."""

        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.yaml = yaml.read_yaml_from_view(self.view)
        except Exception:
            errors = True
            error_msg(self.errors["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

        errors = False
        try:
            # Convert Python dict to PLIST buffer
            if self.save_binary:
                self.output = plist.plist_binary_dumps(
                    self.yaml,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            else:
                self.output = plist.plist_dumps(
                    self.yaml,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            self.yaml = None
        except Exception:
            errors = True
            error_type = 'yaml2bplist' if self.save_binary else 'yaml2plist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def run(self, edit, **kwargs):
        """Begin conversion."""

        if kwargs.get('save_binary', False):
            self.lang = 'bplist_language'
            self.default_lang = 'Packages/Text/Plain text.tmLanguage'
        else:
            self.lang = 'plist_language'
            self.default_lang = 'Packages/XML/XML.tmLanguage'
        super().run(edit, **kwargs)


##########################
# Plist <-> JSON
##########################
class SerializedPlistToJsonCommand(_LanguageConverter):

    """Convert PLIST to JSON."""

    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""
        name = None

        if self.binary:
            setting = 'bplist_json_conversion_ext'
            src = 'bplist'
        else:
            setting = 'plist_json_conversion_ext'
            src = 'plist'

        # Try and find file ext in the ext table
        for ext in self.settings.get(setting, []):
            m = re.match("^(.*)\\." + re.escape(ext[src]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext["json"]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".JSON"
        return name

    def read_source(self):
        """Read the source."""

        errors = False
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            filename = self.view.file_name()
            if self.binary and self.view.encoding() == 'Hexadecimal':
                self.plist = plist.read_plist_from_hex_view(self.view)
            elif self.binary and filename is not None and exists(filename):
                self.plist = plist.read_plist_from_file(filename)
            else:
                self.plist = plist.read_plist_from_view(self.view)
        except Exception:
            errors = True
            error_type = 'view2bplist' if self.binary else 'view2plist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

        errors = False
        try:
            if not errors:
                self.output = json.json_dumps(
                    self.plist,
                    preserve_binary=self.settings.get("json_preserve_binary_data", True)
                )
                self.plist = None
        except Exception:
            errors = True
            error_type = 'bplist2json' if self.binary else 'plist2json'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors


class SerializedJsonToPlistCommand(_LanguageConverter):

    """Convert JSON to PLIST."""

    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""

        name = None

        if self.save_binary:
            setting = 'bplist_json_conversion_ext'
            out = 'bplist'
        else:
            setting = 'plist_json_conversion_ext'
            out = 'plist'

        # Try and find file ext in the ext table
        for ext in self.settings.get(setting, []):
            m = re.match("^(.*)\\." + re.escape(ext["json"]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext[out]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + ".plist"
        return name

    def read_source(self):
        """Read the source."""

        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.json = json.read_json_from_view(self.view)

        except Exception:
            errors = True
            error_msg(self.errors["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

        errors = False
        try:
            # Convert Python dict to PLIST buffer
            if self.save_binary:
                self.output = plist.plist_binary_dumps(
                    self.json,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            else:
                self.output = plist.plist_dumps(
                    self.json,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            self.json = None
        except Exception:
            errors = True
            error_type = 'json2bplist' if self.save_binary else 'json2plist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def run(self, edit, **kwargs):
        """Begin conversion."""

        if kwargs.get('save_binary', False):
            self.lang = 'bplist_language'
            self.default_lang = 'Packages/Text/Plain text.tmLanguage'
        else:
            self.lang = 'plist_language'
            self.default_lang = 'Packages/XML/XML.tmLanguage'
        super().run(edit, **kwargs)


##########################
# YAML <-> JSON
##########################
class SerializedJsonToYamlCommand(_LanguageConverter):

    """Convert JSON to YAML."""

    lang = "yaml_language"
    default_lang = "Packages/YAML/YAML.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""
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

    def read_source(self):
        """Read the source."""

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
            self.json = json.read_json_from_view(self.view)
        except Exception:
            errors = True
            error_msg(self.errors["view2json"], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

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

                self.output = yaml.yaml_dumps(
                    self.json,
                    default_flow_style=default_flow_style,
                    indent=self.settings.get("yaml_indent"),
                    strip_tabs=self.strip_tabs,
                    detect_timestamp=self.settings.get("yaml_detect_timestamp", True)
                )
                self.json = None
        except Exception:
            errors = True
            error_msg(self.errors["json2yaml"], traceback.format_exc())
        return errors


class SerializedYamlToJsonCommand(_LanguageConverter):

    """Convert YAML to JSON."""

    lang = "json_language"
    default_lang = "Packages/JavaScript/JSON.tmLanguage"

    def get_output_file(self, filename):
        """Get output filename to save to."""

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

    def read_source(self):
        """Read the source."""

        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.yaml = yaml.read_yaml_from_view(self.view)
        except Exception:
            errors = True
            error_msg(self.errors["view2yaml"], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = json.json_dumps(
                self.yaml,
                preserve_binary=self.settings.get("json_preserve_binary_data", True)
            )
            self.yaml = None
        except Exception:
            errors = True
            error_msg(self.errors["yaml2json"], traceback.format_exc())
        return errors


##########################
# BPLIST <-> PLIST
##########################
class SerializedPlistToPlistCommand(_LanguageConverter):

    """Convert BPLIST <-> PLIST."""

    lang = 'plist_language'
    default_lang = 'Packages/Text/Plain text.tmLanguage'

    def get_output_file(self, filename):
        """Get output filename to save to."""

        name = None

        # Try and find file ext in the ext table
        if self.binary:
            src = 'bplist'
            out = 'plist'
            default_out = '.plist'
        else:
            src = 'plist'
            out = 'bplist'
            default_out = '.plist'

        for ext in self.settings.get('bplist_plist_conversion_ext', []):
            m = re.match("^(.*)\\." + re.escape(ext[src]) + "$", filename, re.IGNORECASE)
            if m is not None:
                name = m.group(1) + "." + ext[out]
                break

        # Could not find ext in table, replace current extension with default
        if name is None:
            name = splitext(filename)[0] + default_out

        return name

    def read_source(self):
        """Read the source."""

        errors = False
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            filename = self.view.file_name()
            if self.binary and self.view.encoding() == 'Hexadecimal':
                self.plist = plist.read_plist_from_hex_view(self.view)
            elif self.binary and filename is not None and exists(filename):
                self.plist = plist.read_plist_from_file(filename)
            else:
                self.plist = plist.read_plist_from_view(self.view)
        except Exception:
            errors = True
            error_type = 'view2bplist' if self.binary else 'view2plist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def convert(self, edit):
        """Convert the read data to the desired format."""

        errors = False
        try:
            # Convert Python dict to PLIST buffer
            if self.save_binary:
                self.output = plist.plist_binary_dumps(
                    self.plist,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            else:
                self.output = plist.plist_dumps(
                    self.plist,
                    detect_timestamp=self.settings.get("plist_detect_timestamp", True),
                    none_handler=self.settings.get("plist_none_handler", "fail")
                )
            self.plist = None
        except Exception:
            errors = True
            error_type = "bplist2plist" if self.binary else 'plist2bplist'
            error_msg(self.errors[error_type], traceback.format_exc())
        return errors

    def run(self, edit, **kwargs):
        """Begin conversion."""

        if kwargs.get('save_binary', False):
            self.lang = 'bplist_language'
            self.default_lang = 'Packages/Text/Plain text.tmLanguage'
        else:
            self.lang = 'plist_language'
            self.default_lang = 'Packages/XML/XML.tmLanguage'
        super().run(edit, **kwargs)
