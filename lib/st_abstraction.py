from __future__ import absolute_import
import sublime
from .common_include import load_settings


ST3 = int(sublime.version()) >= 3000

if ST3 and sublime.platform() == "linux":
    # Try and load Linux Python2.6 lib.  Default path is for Ubuntu.
    linux_lib = load_settings().get("linux_python2.6_lib", "/usr/lib/python2.6/lib-dynload")
    if not linux_lib in sys.path and exists(linux_lib):
        sys.path.append(linux_lib)


#################
# PLIST
#################
import plistlib

if not ST3:
    import StringIO
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

else:
    plistDumps = lambda obj: plistlib.writePlistToBytes(
        obj
    ).decode('utf-8')
    readPlistFromView = lambda view: plistlib.readPlistFromBytes(
        view.substr(
            sublime.Region(0, view.size())
        ).encode('utf8')
    )

#################
# JSON
#################
import json
from .file_strip.json import sanitize_json

if not ST3:
    jsonDumps = lambda obj: json.dumps(
        obj, sort_keys=True, indent=4, separators=(',', ': ')
    ).decode('raw_unicode_escape')
else:
    jsonDumps = lambda obj: json.dumps(
        obj, sort_keys=True, indent=4, separators=(',', ': ')
    ).encode('utf-8').decode('raw_unicode_escape')

readJsonFromView = lambda view: json.loads(
    sanitize_json(
        view.substr(
            sublime.Region(0, view.size())
        ),
        True
    )
)

#################
# YAML
#################
if ST3:
    from . import yaml3 as yaml
else:
    from . import yaml2 as yaml

# http://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
def _should_use_block(value):
    for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def _my_represent_scalar(self, tag, value, style=None):
    if style is None:
        if _should_use_block(value):
            style='|'
        else:
            style = self.default_style

    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node


def yaml_strip(obj, strip_tabs=False):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = yaml_strip(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = yaml_strip(v)
            count += 1
    elif strip_tabs and isinstance(obj, str):
        obj = obj.replace("\t", "    ").rstrip(" ")

    return obj


yaml.representer.BaseRepresenter.represent_scalar = _my_represent_scalar

yaml.add_representer(
    plistlib._InternalDict,
    yaml.SafeDumper.represent_dict
)

yaml.add_constructor(
    "tag:yaml.org,2002:regex",
    yaml.Loader.construct_yaml_str
)
