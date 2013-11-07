"""
File Strip
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import re
from .comments import Comments


def strip_dangling_commas(text, preserve_lines=False):
    regex = re.compile(
        # ([1st group] dangling commas) | ([8th group] everything else)
        r"""((,([\s\r\n]*)(\]))|(,([\s\r\n]*)(\})))|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|.[^,"']*)""",
        re.MULTILINE | re.DOTALL
    )

    def remove_comma(m, preserve_lines=False):
        if preserve_lines:
            # ,] -> ] else ,} -> }
            return m.group(3) + m.group(4) if m.group(2) else m.group(6) + m.group(7)
        else:
            # ,] -> ] else ,} -> }
            return m.group(4) if m.group(2) else m.group(7)

    return (
        ''.join(
            map(
                lambda m: m.group(8) if m.group(8) else remove_comma(m, preserve_lines),
                regex.finditer(text)
            )
        )
    )


def strip_comments(text, preserve_lines=False):
    return Comments('json', preserve_lines).strip(text)


def sanitize_json(text, preserve_lines=False):
    return strip_dangling_commas(Comments('json', preserve_lines).strip(text), preserve_lines)
