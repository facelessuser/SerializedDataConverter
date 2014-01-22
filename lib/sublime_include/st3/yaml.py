from __future__ import absolute_import
import sublime
from . import pyyaml as yaml
import plistlib

__all__ = ["readYamlFromView", "yamlDumps"]

readYamlFromView = lambda view: yaml.load(
    view.substr(
        sublime.Region(0, view.size())
    )
)

yamlDumps = lambda obj, default_flow_style=None, strip_tabs=False: yaml.dump(
    yaml_strip(obj) if strip_tabs else obj,
    width=None,
    indent=4,
    allow_unicode=True,
    default_flow_style=default_flow_style
)


# Strip tabs and trailing spaces to allow block format to successfully be triggered
def yaml_strip(obj):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = yaml_strip(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = yaml_strip(v)
            count += 1
    elif isinstance(obj, str):
        obj = obj.replace("\t", "    ").rstrip(" ")

    return obj


# Control when to use block style
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


yaml.representer.BaseRepresenter.represent_scalar = _my_represent_scalar


# Handle python dict
yaml.add_representer(
    plistlib._InternalDict,
    yaml.SafeDumper.represent_dict
)

yaml.add_representer(
    plistlib.Data,
    lambda self, data: self.represent_binary(data.data)
)


def binary_constructor(self, node):
    return plistlib.Data(self.construct_yaml_binary(node))


yaml.add_constructor(
    "tag:yaml.org,2002:binary",
    binary_constructor
)

# Add !!Regex support during translation
yaml.add_constructor(
    "tag:yaml.org,2002:regex",
    yaml.Loader.construct_yaml_str
)
