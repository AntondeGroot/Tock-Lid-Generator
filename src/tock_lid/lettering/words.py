"""Laying out a whole word with proper kerning and ligatures."""

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from tock_lid.lettering.fonts import FontFace
from tock_lid.lettering.glyphs import glyph_outline


def word_outline(font: FontFace, word: str) -> BaseGeometry:
    """The word as one shape in font units, y up, starting at the origin."""
    text = word.upper() if font.uppercase else word
    tt_font = TTFont(font.path, fontNumber=font.index)
    glyph_set, glyph_order = tt_font.getGlyphSet(), tt_font.getGlyphOrder()
    pieces, pen_x = [], 0
    for glyph_id, position in _shape(font, text):
        outline = glyph_outline(glyph_set[glyph_order[glyph_id]], glyph_set)
        if not outline.is_empty:
            pieces.append(affinity.translate(outline, pen_x + position.x_offset, position.y_offset))
        pen_x += position.x_advance
    return unary_union(pieces)


def _shape(font: FontFace, text: str):
    """HarfBuzz picks the glyphs and their positions, including kerning."""
    face = hb.Face(hb.Blob.from_file_path(str(font.path)), font.index)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb.Font(face), buffer, {"kern": True, "liga": True})
    glyph_ids = [info.codepoint for info in buffer.glyph_infos]
    return list(zip(glyph_ids, buffer.glyph_positions, strict=True))
