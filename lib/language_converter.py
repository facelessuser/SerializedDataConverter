from __future__ import absolute_import
import sublime
import sublime_plugin
from os.path import exists, basename
import traceback
from .common_include import *
import codecs


ERRORS = {
    "filewrite": "Could not write file!\nPlease see console for more info.",
    "bufferwrite": "Could not write view buffer!\nPlease see console for more info."
}


class LanguageConverter(sublime_plugin.TextCommand):
    lang = None
    default_lang = "Packages/Text/Plain text.tmLanguage"

    def __set_syntax(self):
        if self.output_view is not None:
            # Get syntax language and set it
            syntax = load_settings(self.lang, self.default_lang) if self.lang is not None else self.default_lang
            self.output_view.set_syntax_file(syntax)

    def __write_file(self, edit, show_file):
        errors = False
        # Get current view's filename
        filename = self.view.file_name()
        save_filename = self.get_output_file(filename) if filename is not None and exists(filename) else None

        if save_filename is not None:
            # Save content to UTF file
            try:
                with codecs.open(save_filename, "w", "utf-8") as f:
                    f.write(self.output)
                if show_file:
                    self.output_view = self.view.window().open_file(save_filename)
            except:
                errors = True
                error_msg(ERRORS["filewrite"], traceback.format_exc())
            if not errors and show_file:
                self.__set_syntax()
        else:
            # Could not acquire a name that exists on disk
            # Fallback to buffer write
            self.__write_buffer(edit, force_new_buffer=True)

    def __write_buffer(self, edit, force_new_buffer=False):
        errors = False
        new_buffer = bool(load_settings("open_in_new_buffer", False))

        # Save content to view buffer
        try:
            self.output_view = self.view.window().new_file() if new_buffer or force_new_buffer else self.view
            self.output_view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                self.output
            )
        except:
            errors = True
            error_msg(ERRORS["bufferwrite"], traceback.format_exc())

        if not errors:
            if new_buffer or force_new_buffer:
                # If a name can be acquired from the original view, give buffer a modified derivative of the name
                filename = self.view.file_name()
                buffer_name = basename(self.get_output_file(filename)) if filename is not None else None
                if buffer_name is not None:
                    self.output_view.set_name(buffer_name)
            self.__set_syntax()

    def is_enabled(self, save_to_file=False, force=False):
        enabled = True
        if not force:
            if save_to_file and not bool(load_settings("enable_save_to_file_commands", False)):
                enabled = False
            elif not save_to_file and not bool(load_settings("enable_show_in_buffer_commands", False)):
                enabled = False
        return enabled

    def get_output_file(self, filename):
        return self.view

    def read_buffer(self):
        return False

    def convert(self, edit):
        return False

    def run(self, edit, save_to_file=False, show_file=True, **kwargs):
        if not self.read_buffer():
            if not self.convert(edit):
                if save_to_file:
                    self.__write_file(edit, show_file)
                else:
                    self.__write_buffer(edit)
