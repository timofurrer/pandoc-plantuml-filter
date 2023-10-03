import os
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
        ("single-diagram-with-filename-without-subdirectory", ["\\includegraphics", "example.png"], ["example.png"]),
        (
            "single-diagram-reference",
            ["\\includegraphics", "images/example.png", "\\includegraphics{images/example.png}"],
            ["images/example.png"],
        ),
    ],
)
def test_digrams(mocker, tmp_path, filename, expected_content, expected_files):
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
