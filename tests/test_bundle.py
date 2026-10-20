from zipfile import ZipFile

import pytest
from shapely.geometry import box

from tock_lid import generator
from tock_lid.bundle import write_bundle
from tock_lid.design import LidSpec


@pytest.fixture(autouse=True)
def fake_outlines(monkeypatch):
    monkeypatch.setattr(generator, "word_outline", lambda _font, _word: box(0, 0, 300, 100))


def test_bundle_has_a_preview_and_one_stl_per_colour_named_after_word_and_font(tmp_path):
    zip_path = tmp_path / "lids.zip"
    combinations = [("playball", "standard"), ("spectral-extrabold-italic", "double")]

    write_bundle(zip_path, combinations, ("Tock", "Toc"), LidSpec())

    names = set(ZipFile(zip_path).namelist())
    folder = "tock-lids/spectral-extrabold-italic/double/toc/"
    assert f"{folder}toc-spectral-preview.svg" in names
    assert {name.removeprefix(folder) for name in names if name.startswith(folder)} >= {
        "toc-spectral-fill.stl",
        "toc-spectral-outline-inner.stl",
        "toc-spectral-gap.stl",
        "toc-spectral-outline-outer.stl",
        "toc-spectral-background.stl",
    }
    lid_folders = {name.rsplit("/", 1)[0] for name in names if name.endswith(".stl")}
    assert len(lid_folders) == 2 * 2
