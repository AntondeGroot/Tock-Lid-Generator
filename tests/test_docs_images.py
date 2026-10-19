import os
import subprocess
import sys
from pathlib import Path

import pytest

from tock_lid.lettering import CATALOGUE

REPO_ROOT = Path(__file__).parent.parent
DOCS = REPO_ROOT / "docs"
README_IMAGES = ["fonts.svg", "styles.svg"]
HAS_SYSTEM_FONTS = all(font.path.is_file() for font in CATALOGUE.values())


@pytest.mark.skipif(not HAS_SYSTEM_FONTS, reason="needs the macOS system fonts")
def test_readme_images_match_a_fresh_run_of_the_generate_script(tmp_path):
    environment = {**os.environ, "TOCK_LID": f"{sys.executable} -m tock_lid"}

    subprocess.run(["sh", "docs/generate.sh", tmp_path], cwd=REPO_ROOT, env=environment, check=True)

    for image in README_IMAGES:
        is_unchanged = (tmp_path / image).read_bytes() == (DOCS / image).read_bytes()
        assert is_unchanged, f"docs/{image} is stale; run docs/generate.sh"
