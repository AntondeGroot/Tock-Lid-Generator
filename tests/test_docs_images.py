import os
from pathlib import Path

import pytest

from tock_lid.cli import main
from tock_lid.lettering import CATALOGUE

DOCS = Path(__file__).parent.parent / "docs"
README_IMAGES = ["fonts-everywhere.svg", "fonts-macos.svg", "styles-macos.svg"]
HAS_ALL_FONTS = all(font.is_available for font in CATALOGUE.values())
# Apple ships different font versions per macOS release, and geometry libraries differ per
# machine, so the committed images only reproduce on the machine that made them.
ON_CI = "CI" in os.environ


@pytest.mark.skipif(not HAS_ALL_FONTS, reason="the README images include the macOS system fonts")
@pytest.mark.skipif(ON_CI, reason="the README images are only reproducible on the machine that made them")
def test_readme_images_match_a_fresh_run_of_the_docs_command(tmp_path):
    main(["docs", "--out", str(tmp_path)])

    for image in README_IMAGES:
        is_unchanged = (tmp_path / image).read_bytes() == (DOCS / image).read_bytes()
        assert is_unchanged, f"docs/{image} is stale; run 'tock-lid docs'"
