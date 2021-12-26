#!/usr/bin/env python

"""
Pandoc filter to process code blocks with class "plantuml" into
plant-generated images.
Needs `plantuml.jar` from http://plantuml.com/.
"""

import glob
import os
import re
import sys
import subprocess

from pandocfilters import toJSONFilter, Para, Image
from pandocfilters import get_filename4code, get_caption, get_extension

PLANTUML_BIN = os.environ.get('PLANTUML_BIN', 'plantuml')


def rel_mkdir_symlink(src, dest):
    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if os.path.exists(dest):
        os.remove(dest)

    src = os.path.relpath(src, dest_dir)
    os.symlink(src, dest)


def plantuml(key, value, format_, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "plantuml" in classes:
            caption, typef, keyvals = get_caption(keyvals)

            filename = get_filename4code("plantuml", code)
            filetype = get_extension(format_, "png", html="svg", latex="png")

            src = filename + '.uml'
            dest = filename + '.' + filetype

            # Generate image only once
            if not os.path.isfile(dest):
                txt = code.encode(sys.getfilesystemencoding())
                if not txt.startswith(b"@start"):
                    txt = b"@startuml\n" + txt + b"\n@enduml\n"
                with open(src, "wb") as f:
                    f.write(txt)

                subprocess.check_call(PLANTUML_BIN.split() +
                                      ["-t" + filetype, src])

            # Update symlink each run
            for ind, keyval in enumerate(keyvals):
                if keyval[0] == 'plantuml-filename':
                    link = keyval[1]
                    keyvals.pop(ind)
                    rel_mkdir_symlink(dest, link)
                    dest = link
                    break

            # Get all the generated files - when `page XxY` is used, more than one
            # image is generated. There are in the form '[filename]_00x.[filetype]'
            file_list = glob.glob(filename + '*.' + filetype)

            if len(file_list) == 1:
                return Para([Image([ident, [], keyvals], caption, [dest, typef])])
            else:
                # Case when more than one image has been generated for a plantUML diagram

                # 'page hxv' defines the number of images in the horizontal and vertical direction
                PLANTUML_PAGE_STATEMENT = re.compile(r"page ([0-9]+)x([0-9]+)")

                # Order the file names
                file_list = sorted(file_list)

                # Retrieve how many images are used in the horizontal and vertical directions
                # in this particular piece of plantUML code
                code_lines = [l.strip() for l in code.split('\n')]
                for code_line in code_lines:
                    m = PLANTUML_PAGE_STATEMENT.search(code_line)
                    if m:
                        hpages = int(m.group(1))
                        vpages = int(m.group(2))

                        if hpages != 1:
                            sys.stderr.write(f"Warning: the plantUML image has {hpages} horizontal images. "
                                              "They will need to be displayed on the same line.\n")
                        break

                # Order the image from left to right and top to bottom
                # Note: plantUML generates the images from top to bottom and left to right.
                #       So in a configuration 'page 3x3', the second image on the right will
                #       for instance be 'image_003.png'
                image_list = []
                for v in range(0, vpages):
                    for h in range(0, hpages):
                        index = (h * hpages) + v
                        image_list.append(file_list[index])

                return Para(
                    [Image([ident, [], keyvals], caption, [image_filename, typef]) for image_filename in image_list]
                )


def main():
    toJSONFilter(plantuml)


if __name__ == "__main__":
    main()
