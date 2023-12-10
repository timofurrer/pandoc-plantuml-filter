import os
import re
import subprocess

from pathlib import Path

import pytest

__TEST_BASE_DIR__ = Path(os.path.dirname(__file__)) / "testdata"


@pytest.mark.parametrize(
    "filename, expected_content, expected_files",
    [
        ("single-diagram", ["\\includegraphics{plantuml-images/"], []),
        ("single-diagram-with-config", ["\\includegraphics", "width=0.6"], []),
        (
            "single-diagram-with-filename-and-subdirectory",
            ["\\includegraphics", "images/example.png"],
            ["images/example.png"],
        ),
        (
            "single-diagram-with-filename-without-subdirectory",
            ["\\includegraphics", "example.png"],
            ["example.png"],
        ),
        (
            "single-diagram-reference",
            [
                "\\includegraphics",
                "images/example.png",
                "\\includegraphics{images/example.png}",
            ],
            ["images/example.png"],
        ),
    ],
)
def test_digrams(tmp_path, filename, expected_content, expected_files):
    input_file = str(__TEST_BASE_DIR__ / f"{filename}.md")
    output_file = str(tmp_path / f"{filename}.tex")

    cmd = subprocess.run(["pandoc", input_file, "-o", output_file, "--filter", "pandoc-plantuml"])
    assert cmd.returncode == 0

    with open(output_file) as f:
        content = f.read()

    for line in expected_content:
        assert line in content

    for file in expected_files:
        assert os.path.exists(file)


def test_filetype_param_from_meta(tmp_path):
    input_file = str(__TEST_BASE_DIR__ / "single-diagram-with-meta.md")
    output_file = str(tmp_path / "single-diagram-with-meta.tex")

    cmd = subprocess.run(["pandoc", input_file, "-o", output_file, "--filter", "pandoc-plantuml"])
    assert cmd.returncode == 0

    with open(output_file) as f:
        content = f.read()

    pattern = re.compile(r"plantuml-images\/.*\.svg")
    match = pattern.search(content)
    assert match


def test_filetype_metadata_is_overridden_from_cli(tmp_path):
    input_file = str(__TEST_BASE_DIR__ / "single-diagram-with-meta.md")
    output_file = str(tmp_path / "single-diagram-with-meta.tex")
    args = ["--metadata=plantuml-format:jpg"]

    cmd = subprocess.run(["pandoc", input_file, "-o", output_file, "--filter", "pandoc-plantuml"] + args)
    assert cmd.returncode == 0

    with open(output_file) as f:
        content = f.read()

    pattern = re.compile(r"plantuml-images\/.*\.jpg")
    match = pattern.search(content)
    assert match
