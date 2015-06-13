# User Guide {: .doctitle}
Configuration and usage of SerializedDataConverter.

---

## Commands
All commands are accessible via the command palette.  Comments are not preserved during conversion.

### Serialized Data Converter: (Type A) to (Type B)
Command that converts an open (JSON|PLIST|BPLIST|YAML) file to (JSON|PLIST|BPLIST|YAML). It will strip C style comments and also try and catch forgotten trailing commas for JSON source files if converting from JSON.

Note that when reading a BPLIST (binary PLIST), the encoding must be `Hexadecimal` or the view must be a file that exists on disk so that the raw, un-encoded data can be acquired as encoding can cause data to be lost.

### Serialized Data Converter: Save (Type A) to (Type B)
Command that converts an open (JSON|PLIST|BPLIST|YAML) file to (JSON|PLIST|BPLIST|YAML) and saves it to the respective file type.  File name is determined by the appropriate setting (`plist_json_conversion_ext`|`plist_yaml_conversion_ext`|`json_yaml_conversion_ext`|`bplist_json_conversion_ext`|`bplist_yaml_conversion_ext`|`bplist_plist_conversion_ext`).  It will strip C style comments and also try and catch forgotten trailing commas for JSON source files if converting from JSON. If the file to convert does not exist on disk, the converted file will not initially exist either, but it will only be shown in the view buffer until saved manually.

Note that when reading a BPLIST (binary PLIST), the encoding must be `Hexadecimal` or the view must be a file that exists on disk so that the raw, un-encoded data can be acquired as encoding can lose some of the data.

## Settings
SerializedDataConverter has a number of settings that can be configured.

### enable_save_to_file_commands
Allows the disabling of the "save to file" commands in the command palette.

```js
    // Enable creation of new file based on extension map containing the converted data
    // If the current file to convert does not exist on disk, the converted file will default
    // To being shown in a view buffer only, and will not be automatically saved to disk.
    "enable_save_to_file_commands": true,
```

### enable_show_in_buffer_commands
Allows the disabling of the "show conversion in view buffer" commands in the command palette.

```js
    // Enable show conversion in a view buffer
    "enable_show_in_buffer_commands": true,
```

### open_in_new_buffer
When a "show conversion in view buffer" command is executed, this will force the conversion to show up in its own new view buffer.

```js
    // When converting buffer open conversion in new buffer
    "open_in_new_buffer": true,
```

### (Type A)\_(Type B)\_conversion_ext
Allows you to provide a file name conversion mapping from any type extension to a another type extension and vice versa.  They are evaluated in the order they appear.  The name of the setting denotes which file type to which file the conversion rules apply to.  The mapping rules are defined by using the file type as the key, and the desired extension as the value.  The mapping works both ways, so if the name is `plist_json_conversion_ext`, then it will convert in either direction; either PLIST --> JSON or JSON --> PLIST.

```js
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

### (Type)\_language
Allows the selection of a given language file to be used for the converted buffer or file.

```javascript
    // Languages to use on conversion
    "json_language": "Packages/JavaScript/JSON.tmLanguage",
    "yaml_language": "Packages/YAML/YAML.tmLanguage",
    "plist_language": "Packages/XML/XML.tmLanguage",
    "bplist_language": "Packages/Text/Plain text.tmLanguage",
```

### convert_on_save
When a file with the specified extension is saved, the plugin will automatically run the conversion command on the file and save the converted form to the disk.

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

### yaml_strip_tabs_from
These are language extensions in which the converter will strip tabs from to ensure multi-lines aren't quoted with "\t".  It also strips trailing spaces from multi-line strings. This helps multi-line strings convert in a pretty format (does not guarantee all values will be convert to a pretty format, but increases the odds). If you are having trouble converting a file and getting a 1:1 translation, remove the file type.

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

### yaml_default_flow_style
Lets you control the YAML output flow style.

```js
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

### yaml_detect_timestamp
Detects python datetime objects when converting to YAML and will convert them to the appropriate syntax for YAML.

```js
    // Detect timestamps on conversion for yaml
    "yaml_detect_timestamp": true,
```

### plist_detect_timestamp
When converting to PLIST, this will instruct the library to detect python datetime objects and convert them appropriately for PLIST.

```js
    // Detect timestamps on conversion for plists
    "plist_detect_timestamp": true,
```

### json_preserve_binary_data
When converting to JSON, binary types will be preserved as a special type so that when converting to YAML or PLIST, the data can be preserved.  The JSON spec doesn't really support binary types natively.

```js
    // Preserve binary data when converting to JSON
    // This will create binary data in this form which
    // will be recongnized and representing in plist and yaml native binary format:
    //    {
    //        "!!python/object:plistlib.Data": "U29tZSBkYXRh"
    //    }
    "json_preserve_binary_data": true,
```

### plist_none_handler
Sets how SerializedDataConverter will handle a `None` (or null) type when converting to PLIST.

| Mode | Description |
|------|-------------|
| fail | This will let the conversion fail as null types are not in the spec. |
| false | This will convert null types to the boolean value of `false`. |
| strip | This will remove the null type attribute all together. |

```js
    // When converting to a plist, and the structure contains none, the plugin should:
    //    - "fail": let the conversion fail
    //    - "false": set the None objects to False
    //    - "strip": strip the None members from the structure
    "plist_none_handler": "fail"
```

## Linux Issues (ST2 only)
I have provided a fix for Ubuntu.  Ubuntu requires a full install of Python2.6, but it only comes with a minimal install by default.  You can enter the command below in your linux terminal to get the full install.

`sudo apt-get install python2.6`

I have provided the Python lib path in the settings file so it may be adapted for other distros in needed.

`"linux_python2.6_lib": "/usr/lib/python2.6/lib-dynload"`
