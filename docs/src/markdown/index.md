# SerializedDataConverter

Convert between serialized data formats (plist | bplist | json | yaml)

## Third Party Libraries

- pyyaml: https://github.com/yaml/pyyaml
- plistlib: Sublime Text 3 currently uses Python 3.3, but Python 3.4 has a new version of plistlib that handles binary
plists.  To get this functionality, we dropped the [Python 3.4 plistlib](https://hg.python.org/cpython/file/3.4/Lib/plistlib.py)
directly into the plugin with minor changes to get it working in Python 3.3.  Eventually this will be removed if Sublime
moves to Python 3.4.
