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

PLANTUML_BIN = os.environ.get("PLANTUML_BIN", "plantuml")


def rel_mkdir_symlink(src, dest):
    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if os.path.exists(dest):
        os.remove(dest)

    src = os.path.relpath(src, dest_dir)
    os.symlink(src, dest)


def calculate_filetype(format_, plantuml_format):
    if plantuml_format:
        # File-type is overwritten via cli
        # --metadata=plantuml-format:svg
        if plantuml_format["t"] == "MetaString":
            return get_extension(format_, plantuml_format["c"])
        # File-type is overwritten in the meta data block of the document
        # ---
        # plantuml-format: svg
        # ---
        elif plantuml_format["t"] == "MetaInlines":
            return get_extension(format_, plantuml_format["c"][0]["c"])

    # Default per output-type eg. output-type: html -> file-type: svg
    return get_extension(format_, "png", html="svg", latex="png")


def plantuml(key, value, format_, meta):
    if key == "CodeBlock":
        [[ident, classes, keyvals], code] = value

        if "plantuml" in classes:
            caption, typef, keyvals = get_caption(keyvals)

            filename = get_filename4code("plantuml", code)
            filetype = calculate_filetype(format_, meta.get("plantuml-format"))

            src = filename + ".uml"
            dest = filename + "." + filetype

            # Generate image only once
            if not os.path.isfile(dest):
                txt = code.encode(sys.getfilesystemencoding())
                if not txt.startswith(b"@start"):
                    txt = b"@startuml\n" + txt + b"\n@enduml\n"
                with open(src, "wb") as f:
                    f.write(txt)

                subprocess.check_call(PLANTUML_BIN.split() + ["-t" + filetype, src])
                sys.stderr.write("Created image " + dest + "\n")

            # Update symlink each run
            for ind, keyval in enumerate(keyvals):
                if keyval[0] == "plantuml-filename":
                    link = keyval[1]
                    keyvals.pop(ind)
                    rel_mkdir_symlink(dest, link)
                    dest = link
                    break

            return Para([Image([ident, [], keyvals], caption, [dest, typef])])


def main():
    toJSONFilter(plantuml)


if __name__ == "__main__":
    main()
