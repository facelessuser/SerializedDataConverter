from . import yaml
import plistlib


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

yaml.add_representer(
    plistlib._InternalDict,
    yaml.SafeDumper.represent_dict
)

yaml.add_constructor(
    "tag:yaml.org,2002:regex",
    yaml.Loader.construct_yaml_str
)
