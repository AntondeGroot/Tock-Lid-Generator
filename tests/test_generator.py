import pytest
from shapely.geometry import box

from tock_lid import generator
from tock_lid.design import STYLES, LidSpec
from tock_lid.generator import LidSet, design_lids
from tock_lid.lettering import FontFace

# Same letter height in font units; only the word length differs.
FAKE_OUTLINES = {"Keezen": box(0, 0, 600, 100), "Toc": box(0, 0, 300, 100)}


@pytest.fixture
def fake_font(monkeypatch):
    monkeypatch.setattr(generator, "word_outline", lambda _font, word: FAKE_OUTLINES[word])
    return FontFace("fake", path=None)


def test_all_words_in_a_set_get_the_same_letter_size(fake_font):
    lid_set = LidSet(fake_font, STYLES["standard"], ("Keezen", "Toc"), LidSpec())

    lids = design_lids(lid_set)

    letter_heights = {word: _height(layers[0].shape) for word, layers in lids.items()}
    assert letter_heights["Keezen"] == pytest.approx(letter_heights["Toc"])


def _height(shape) -> float:
    _, min_y, _, max_y = shape.bounds
    return max_y - min_y
