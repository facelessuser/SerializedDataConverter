from __future__ import absolute_import
import sublime
from . import pyyaml as yaml
import base64
import plistlib
import datetime
import re

__all__ = ["readYamlFromView", "yamlDumps", "yaml_strip"]

# http://yaml.org/type/timestamp.html
YAML_TIMESTAMP = re.compile(
    r'''
        ([0-9][0-9][0-9][0-9]) # (year)
        -([0-9][0-9]?)         # (month)
        -([0-9][0-9]?)         # (day)
        (?:
            (?:(?:[Tt]|[ \t]+)([0-9][0-9]?))                   # (hour)
            :([0-9][0-9])                                      # (minute)
            :([0-9][0-9])                                      # (second)
            (?:\.([0-9]*))?                                    # (fraction)
            (?:[ \t]*Z|([-+])([0-9][0-9]?)(?::([0-9][0-9]))?)? # (time zone)
        )?
    ''',
    re.VERBOSE
)


readYamlFromView = lambda view: yaml.load(
    view.substr(
        sublime.Region(0, view.size())
    )
)

yamlDumps = lambda obj, default_flow_style=None, strip_tabs=False, detect_timestamp=False: yaml.dump(
    yaml_convert_to(obj, strip_tabs, detect_timestamp),
    width=None,
    indent=4,
    allow_unicode=True,
    encoding='utf-8',
    default_flow_style=default_flow_style,
    Dumper=yaml.Dumper
).decode('utf-8')


def convert_timestamp(obj):
    delta = None
    time_stamp = None
    m = YAML_TIMESTAMP.match(obj)
    if m is not None:
        # Date object
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if m.group(4) is None:
            time_stamp = datetime.date(year, month, day)
        else:
            # Time object
            hour = int(m.group(4))
            minute = int(m.group(5))
            second = int(m.group(6))

            # Keep fraction 6 digits long if found
            if m.group(7) is not None:
                fraction_string = m.group(7)[:6]
                fraction = int(fraction_string + ("0" * (6 - len(fraction_string))))
            else:
                fraction = 0

            # Adjust for timezone
            if m.group(8) is not None:
                tz_hour = int(m.group(9))
                tz_minute = int(m.group(10)) if m.group(10) is not None else 0
                delta = datetime.timedelta(hours=tz_hour, minutes=tz_minute) * (-1 if m.group(8) == "-" else 1)
            else:
                delta = None

            time_stamp = datetime.datetime(year, month, day, hour, minute, second, fraction)

    return time_stamp if delta is None else time_stamp - delta


def yaml_convert_to(obj, strip_tabs=False, detect_timestamp=False):
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = yaml_convert_to(v, strip_tabs, detect_timestamp)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = yaml_convert_to(v, strip_tabs, detect_timestamp)
            count += 1
    elif isinstance(obj, basestring):
        if detect_timestamp:
            converted = False
            time_stamp = convert_timestamp(obj)
            if time_stamp is not None:
                obj = time_stamp
                converted = True
        elif strip_tabs and not converted:
            obj = obj.replace("\t", "    ").rstrip(" ")

    return obj


# Control when to use block style
# http://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
def _should_use_block(value):
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
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


# Handle Unicode
yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:str', value))


# Handle Timestamps
def timestamp_constructor(self, node):
    timestamp = self.construct_yaml_timestamp(node)
    if type(timestamp) is not datetime.datetime:
        timestamp = str(timestamp)
    else:
        timestamp = '%(year)04d-%(month)02d-%(day)02dT%(hour)02d:%(minute)02d:%(second)02d%(microsecond)sZ' % {
            "year": timestamp.year,
            "month": timestamp.month,
            "day": timestamp.day,
            "hour": timestamp.hour,
            "minute": timestamp.minute,
            "second": timestamp.second,
            "microsecond": ".%06d" % timestamp.microsecond if timestamp.microsecond != 0 else ""
        }
    return timestamp


yaml.add_constructor(
    'tag:yaml.org,2002:timestamp',
    timestamp_constructor
)


# Handle Plist Binary Data
yaml.add_representer(
    plistlib.Data,
    lambda self, data: self.represent_scalar(u'tag:yaml.org,2002:binary', base64.encodestring(data.data), style='|')
)


def binary_constructor(self, node):
    return plistlib.Data(self.construct_yaml_binary(node))


yaml.add_constructor(
    "tag:yaml.org,2002:binary",
    binary_constructor
)


# Handle python dict
yaml.add_representer(
    plistlib._InternalDict,
    lambda self, data: self.represent_mapping(u'tag:yaml.org,2002:map', data)
)


# Add !!Regex support during translation
yaml.add_constructor(
    "tag:yaml.org,2002:regex",
    yaml.Loader.construct_yaml_str
)
