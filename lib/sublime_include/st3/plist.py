import sublime
import plistlib

__all__ = ["readPlistFromView", "plistDumps"]

plistDumps = lambda obj: plistlib.writePlistToBytes(
    obj
).decode('utf-8')

readPlistFromView = lambda view: plistlib.readPlistFromBytes(
    view.substr(
        sublime.Region(0, view.size())
    ).encode('utf8')
)
