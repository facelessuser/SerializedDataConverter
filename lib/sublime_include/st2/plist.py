import sublime
import plistlib
import StringIO

__all__ = ["readPlistFromView", "plistDumps"]

plistDumps = lambda obj: plistlib.writePlistToString(
    obj
).decode('utf-8')

readPlistFromView = lambda view: plistlib.readPlist(
    StringIO.StringIO(
        view.substr(
            sublime.Region(0, view.size())
        ).encode('utf8')
    )
)
