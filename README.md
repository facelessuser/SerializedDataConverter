[![Donate via PayPal][donate-image]][donate-link]
[![Package Control Downloads][pc-image]][pc-link]
![License][license-image]
# SerializedDataConverter
Convert between serialized data formats (plist | bplist | json | yaml)

# Third Party Libraries

- pyyaml: https://github.com/yaml/pyyaml
- plistlib: Sublime Text 3 currently uses Python 3.3, but Python 3.4 has a new version of plistlib that handles binary plists.  To get this functionality, we dropped the [Python 3.4 plistlib](https://hg.python.org/cpython/file/3.4/Lib/plistlib.py) directly into the plugin with minor changes to get it working in Python 3.3.  Eventually this will be removed if Sublime moves to Python 3.4.

# Documentation
http://facelessuser.github.io/SerializedDataConverter/

# License
MIT except for PYYAML and plistlib.  See LICENSE for more info.

[pc-image]: https://img.shields.io/packagecontrol/dt/SerializedDataConverter.svg?labelColor=333333&logo=sublime%20text
[pc-link]: https://packagecontrol.io/packages/SerializedDataConverter
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
[donate-image]: https://img.shields.io/badge/Donate-PayPal-3fabd1?logo=paypal
[donate-link]: https://www.paypal.me/facelessuser
