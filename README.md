SerializedDataConverter
=======================

Convert between serialized data formats (plist | bplist | json | yaml)

<img src="https://dl.dropboxusercontent.com/u/342698/SerializedDataConverter/Example.png" border="0">

# Usage
All commands are accessible via the command palette.  Comments are not preserved during conversion.

## Serialized Data Converter: (Type A) to (Type B)
Command that converts an open (JSON|PLIST|BPLIST|YAML) file to (JSON|PLIST|BPLIST|YAML). It will strip C style comments and also try and catch forgotten trailing commas for JSON source files if converting from JSON.

Note that when reading a BPLIST (binary PLIST), the encoding must be `Hexadecimal` or the view must be a file that exists on disk so that the raw, un-encoded data can be acquired as encoding can lose some of the data.

## Serialized Data Converter: Save (Type A) to (Type B)
Command that converts an open (JSON|PLIST|BPLIST|YAML) file to (JSON|PLIST|BPLIST|YAML) and saves it to the respective file type.  File name is determined by the respective setting (`plist_json_conversion_ext`|`plist_yaml_conversion_ext`|`json_yaml_conversion_ext`).  It will strip C style comments and also try and catch forgotten trailing commas for JSON source files if converting from JSON. If the file to convert does not exist on disk, the converted file will not initially exist either, but it will only be shown in the view buffer until saved manually.

Note that when reading a BPLIST (binary PLIST), the encoding must be `Hexadecimal` or the view must be a file that exists on disk so that the raw, un-encoded data can be acquired as encoding can lose some of the data.

# Settings
## enable\_save\_to\_file\_commands
Allows the disabling of the "save to file" commands in the command palette

## enable\_show\_in\_buffer\_commands
Allows the disabling of the "show conversion if view buffer" commands in the command palette

## open\_in\_new\_buffer
When a "show conversion in view buffer" command is executed, this will force the conversion to show up in its own new view buffer.

## (Type A)\_(Type B)\_conversion_ext
Allows you to provide a file name conversion mapping from any type extension to a another type extension and vice versa.  They are evaluated in the order they appear.  The name of the setting denotes which file type to which file the conversion rules apply to.  The mapping rules are defined by using the file type as the key, and the desired extension as the value.  The mapping works both ways.

```javascript
    // When saving converted data to a file, or when opening
    // conversion in new buffer use these extension maps for file name.
    // Extensions will be evaluated in the order listed below.
    // If the file does not match any of the extensions, the current
    // extension will be replaced with either "plist", "json", or "yaml" accordingly.
    "plist_json_conversion_ext": [
        {"plist": "tmLanguage", "json": "tmLanguage.JSON"},
        {"plist": "tmPreferences", "json": "tmPreferences.JSON"},
        {"plist": "tmTheme", "json": "tmTheme.JSON"}
    ],

    "plist_yaml_conversion_ext": [
        {"plist": "tmLanguage", "yaml": "tmLanguage.YAML"},
        {"plist": "tmPreferences", "yaml": "tmPreferences.YAML"},
        {"plist": "tmTheme", "yaml": "tmTheme.YAML"}
    ],

    "bplist_json_conversion_ext": [
    ],

    "bplist_yaml_conversion_ext": [
    ],

    "bplist_plist_conversion_ext": [
    ],

    "json_yaml_conversion_ext": [
        // Nothing to see here; move along
        // Add your rules here
        //{"json": "some extension", "yaml": "some extension"}
    ],
```

## (Type)\_language
Allows the selection of a given language file to be used for the converted buffer or file.

```javascript
    // Languages to use on conversion
    "json_language": "Packages/JavaScript/JSON.tmLanguage",
    "yaml_language": "Packages/YAML/YAML.tmLanguage",
    "plist_language": "Packages/XML/XML.tmLanguage",
    "bplist_language": "Packages/Text/Plain text.tmLanguage",
```

## convert\_on\_save
When a file with the specified extension is saved, the plugin will automatically run the conversion command on the file to save the converted form to disk as well.

```javascript
    "convert_on_save": [
        // Enable or add what you would like
        // {"ext": "tmLanguage.JSON", "command": "json_to_plist"},
        // {"ext": "tmPreferences.JSON", "command": "json_to_plist"},
        // {"ext": "tmTheme.JSON", "command": "json_to_plist"},
        // {"ext": "tmLanguage.YAML", "command": "yaml_to_plist"},
        // {"ext": "tmPreferences.YAML", "command": "yaml_to_plist"},
        // {"ext": "tmTheme.YAML", "command": "yaml_to_plist"}
    ],
```

# yaml\_strip\_tabs_from
These are language extensions in which the converter will strip tabs from to ensure multilines aren't quoted with "\t".  It also strips trailing spaces from multi-line strings. This helps multiline strings convert in a pretty format (does not guaruntee all values will be convert to a pretty format, but increases the odds). If you are having trouble converting a file and getting a 1:1 translation, remove the file type.

```javascript
    "yaml_strip_tabs_from": [
        "tmLanguage",
        "tmTheme",
        "tmPreferences",
        "tmLanguage.JSON",
        "tmTheme.JSON",
        "tmPreferences.JSON"
    ],
```

# yaml\_default\_flow_style
Lets you control the yaml output flow style.

```javascript
    // In most this should be left to "false" for easy reading, but feel free to change it
    // (none | true | false)
    // none shows things like this will (pretty good):
    //     '1': {name: something}
    // false like this (cleanest to read):
    //     '1':
    //         name: something
    // true will have everything like this (harder to read):
    //     {'1': {name: something}}

    "yaml_default_flow_style": "false"
```

# Other Conversion Controls
There are some other knobs exposed allowing you to affect the conversion; they are listed below:

```javascript
    // Detect timestamps on conversion for yaml
    "yaml_detect_timestamp": true,

    // Detect timestamps on conversion for plists
    "plist_detect_timestamp": true,

    // Preserve binary data when converting to JSON
    // This will create binary data in this form which
    // will be recongnized and representing in plist and yaml native binary format:
    //    {
    //        "!!python/object:plistlib.Data": "U29tZSBkYXRh"
    //    }
    "json_preserve_binary_data": true,

    // When converting to a plist, and the structure contains none, the plugin should:
    //    - "fail": let the conversion fail
    //    - "false": set the None objects to False
    //    - "strip": strip the None members from the structure
    "plist_none_handler": "fail"
```

# Linux Issues (ST2 only)
I have provided a fix for Ubuntu.  Ubuntu requires a full install of Python2.6, but it only comes with a minimal install by default.  You can enter the command below in your linux terminal to get the full install.

`sudo apt-get install python2.6`

I have provided the Python lib path in the settings file so it may be adapted for other distros in needed.

`"linux_python2.6_lib": "/usr/lib/python2.6/lib-dynload"`

# Third Party Libraries

- pyyaml: https://github.com/yaml/pyyaml

# License

SerializedDataConverter is released under the MIT license.

Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
