#!/usr/bin/env python

"""
Pandoc filter to process code blocks with class "plantuml" into
plant-generated images.
Needs `plantuml.jar` from http://plantuml.com/.
"""

import os
import sys
import subprocess

from pandocfilters import toJSONFilter, Para, Image
from pandocfilters import get_filename4code, get_caption, get_extension

PLANTUML_BIN = os.environ.get('PLANTUML_BIN', 'plantuml')


def plantuml(key, value, format_, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "plantuml" in classes:
            caption, typef, keyvals = get_caption(keyvals)

            filename = get_filename4code("plantuml", code)
            filetype = get_extension(format_, "png", html="svg", latex="png")

            src = filename + '.uml'
            dest = filename + '.' + filetype

            if not os.path.isfile(dest):
                txt = code.encode(sys.getfilesystemencoding())
                if not txt.startswith(b"@start"):
                    txt = b"@startuml\n" + txt + b"\n@enduml\n"
                with open(src, "wb") as f:
                    f.write(txt)

                subprocess.check_call(PLANTUML_BIN.split() + ["-t" + filetype, src])
                sys.stderr.write('Created image ' + dest + '\n')

            return Para([Image([ident, [], keyvals], caption, [dest, typef])])


def main():
    toJSONFilter(plantuml)


if __name__ == "__main__":
    main()
