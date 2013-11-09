import sublime
import sublime_plugin
if int(sublime.version()) >= 3000:
    from .lib.common_include import *
else:
    from lib.common_include import *


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
        return load_settings("convert_on_save", [])

    def convert(self, view, command):
        view.run_command("serialized_%s" % command, {"save_to_file": 'True', "show_file": False, "force": True})
