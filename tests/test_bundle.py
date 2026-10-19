from zipfile import ZipFile

import pytest
from shapely.geometry import box

from tock_lid import generator
from tock_lid.bundle import write_bundle
from tock_lid.design import LidSpec


@pytest.fixture(autouse=True)
def fake_outlines(monkeypatch):
    monkeypatch.setattr(generator, "word_outline", lambda _font, _word: box(0, 0, 300, 100))


def test_bundle_has_a_preview_and_one_stl_per_colour_for_every_lid(tmp_path):
    zip_path = tmp_path / "lids.zip"

    write_bundle(zip_path, [("bodoni", "standard"), ("didot", "double")], ("Tock", "Toc"), LidSpec())

    names = set(ZipFile(zip_path).namelist())
    assert "tock-lids/didot/double/toc/toc-preview.svg" in names
    double_toc_stls = {
        name.rsplit("/", 1)[1] for name in names if name.startswith("tock-lids/didot/double/toc/")
    }
    assert double_toc_stls >= {
        "toc-fill.stl",
        "toc-outline-inner.stl",
        "toc-gap.stl",
        "toc-outline-outer.stl",
        "toc-background.stl",
    }
    lid_folders = {name.rsplit("/", 1)[0] for name in names if name.endswith(".stl")}
    assert len(lid_folders) == 2 * 2
