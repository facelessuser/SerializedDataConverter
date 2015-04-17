import sublime
import datetime
from . import pyyaml as yaml
from . import plistlib
import re

__all__ = ["readYamlFromView", "yamlDumps"]

# http://yaml.org/type/timestamp.html
YAML_TIMESTAMP = re.compile(
    r'''
        (?P<year>[0-9][0-9][0-9][0-9])               # year
        -(?P<month>[0-9][0-9]?)                      # month
        -(?P<day>[0-9][0-9]?)                        # day
        (?:
            (?:(?:[Tt]|[ \t]+)(?P<hour>[0-9][0-9]?)) # hour
            :(?P<minute>[0-9][0-9])                  # minute
            :(?P<second>[0-9][0-9])                  # second
            (?:\.(?P<microsecond>[0-9]*))?           # microsecond
            (?:
                [ \t]*Z
                | (?:
                    (?P<tz_sign>[-+])                 # time zone sign
                    (?P<tz_hour>[0-9][0-9]?)          # time zone hour
                    (?::(?P<tz_minute>[0-9][0-9]))?   # time zone minute
                )
            )?
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
    default_flow_style=default_flow_style
)


def convert_timestamp(obj):
    """ Convert YAML timestamp format """
    delta = None
    time_stamp = None
    m = YAML_TIMESTAMP.match(obj)
    if m is not None:
        g = m.groupdict()
        # Date object
        year = int(g["year"])
        month = int(g["month"])
        day = int(g["day"])
        if g["hour"] is None:
            time_stamp = datetime.date(year, month, day)
        else:
            # Time object
            hour = int(g["hour"])
            minute = int(g["minute"])
            second = int(g["second"])

            # Keep microsecond 6 digits long if found
            if g["microsecond"] is not None:
                micro_string = g["microsecond"][:6]
                microsecond = int(micro_string + ("0" * (6 - len(micro_string))))
            else:
                microsecond = 0

            # Adjust for timezone
            if g["tz_sign"] is not None:
                tz_hour = int(g["tz_hour"])
                tz_minute = int(g["tz_minute"]) if g.tz_minute is not None else 0
                delta = datetime.timedelta(hours=tz_hour, minutes=tz_minute) * (-1 if g["tz_sign"] == "-" else 1)
            else:
                delta = None

            time_stamp = datetime.datetime(year, month, day, hour, minute, second, microsecond)

    return time_stamp if delta is None else time_stamp - delta


def yaml_convert_to(obj, strip_tabs=False, detect_timestamp=False):
    """ Convert specific serialized objects before converting to YAML """
    if isinstance(obj, (dict, plistlib._InternalDict)):
        for k, v in obj.items():
            obj[k] = yaml_convert_to(v, strip_tabs, detect_timestamp)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = yaml_convert_to(v, strip_tabs, detect_timestamp)
            count += 1
    elif isinstance(obj, str):
        if detect_timestamp:
            converted = False
            time_stamp = convert_timestamp(obj)
            if time_stamp is not None:
                obj = time_stamp
                converted = True
        elif strip_tabs and not converted:
            obj = obj.replace("\t", "    ").rstrip(" ")

    return obj


def _should_use_block(value):
    """
    Control when to use block style
    http://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    """
    for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def _my_represent_scalar(self, tag, value, style=None):
    """ Scalar """
    if style is None:
        if _should_use_block(value):
            style = '|'
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
    lambda self, data: self.represent_dict(data)
)


# Handle binary data
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


def timestamp_constructor(self, node):
    """ Constructor for YAML timestamp """
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

# Add !!Regex support during translation
yaml.add_constructor(
    "tag:yaml.org,2002:regex",
    yaml.Loader.construct_yaml_str
)
