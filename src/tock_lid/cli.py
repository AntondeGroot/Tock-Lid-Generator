"""Command line: list fonts and styles, generate lid files, or draw a comparison sheet."""

import argparse
import logging
from pathlib import Path

from tock_lid.bundle import every_font_and_style, write_bundle
from tock_lid.design import STYLES, LidSpec, find_style, thin_layers
from tock_lid.export import overview_svg, write_svg
from tock_lid.generator import LidSet, design_lids, write_lid_files
from tock_lid.lettering import FontFace, available_fonts, file_label, find_font, font_from_file
from tock_lid.previews import overview_rows, write_preview_sheets

DEFAULT_WORDS = ["Keezen", "Tock", "Toc"]
# The favourite where it exists (macOS), otherwise the free font chosen to stand in for it.
DEFAULT_FONT_CHOICES = ("snell", "playball")


def main(argv: list[str] | None = None) -> None:
    # fontTools warns about harmless quirks in some system fonts; they are not the user's concern.
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    args = _parser().parse_args(argv)
    try:
        args.command(args)
    except (ValueError, OSError) as error:  # bad input, or a folder that cannot be written
        raise SystemExit(f"error: {error}") from None


def list_fonts(_args) -> None:
    for key, font in available_fonts().items():
        origin = "free, ships with tock-lid" if font.is_bundled else "macOS system font"
        print(f"{key:30} {font.name:30} {origin}")


def list_styles(_args) -> None:
    for key, style in STYLES.items():
        print(f"{key:12} {style.describe()}")


def generate(args) -> None:
    lid, style = _lid_spec(args), find_style(args.style)
    lid_set = LidSet(_chosen_font(args), style, tuple(args.words), lid)
    for word, layers in design_lids(lid_set).items():
        folder = write_lid_files(word, _font_label(args), layers, lid, args.out)
        print(f"{word}: {folder.resolve()}")
        _warn_about_thin_parts(layers, lid)


def overview(args) -> None:
    lid = _lid_spec(args)
    rows = overview_rows(tuple(args.fonts), tuple(args.styles), tuple(args.words), lid)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_svg(args.out, overview_svg(rows, lid))
    print(args.out.resolve())


def docs(args) -> None:
    for path in write_preview_sheets(args.out, tuple(args.words), _lid_spec(args)):
        print(path.resolve())


def bundle(args) -> None:
    write_bundle(args.out, every_font_and_style(), tuple(args.words), _lid_spec(args))
    print(args.out.resolve())


def _chosen_font(args) -> FontFace:
    if args.font_file:
        return font_from_file(args.font_file, args.font_index)
    return find_font(args.font)


def _font_label(args) -> str:
    return file_label(args.font_file.stem if args.font_file else args.font)


def _default_font_key() -> str:
    fonts_here = available_fonts()
    return next(key for key in DEFAULT_FONT_CHOICES if key in fonts_here)


def _lid_spec(args) -> LidSpec:
    return LidSpec(diameter_mm=args.diameter, margin_mm=args.margin, thickness_mm=args.thickness)


def _warn_about_thin_parts(layers, lid: LidSpec) -> None:
    for name, area in thin_layers(layers, lid.min_line_mm).items():
        print(f"  warning: {name} has a {area:.2f} mm² spot thinner than {lid.min_line_mm} mm")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tock-lid", description=__doc__)
    commands = parser.add_subparsers(required=True)
    commands.add_parser("fonts", help="list the built-in fonts").set_defaults(command=list_fonts)
    commands.add_parser("styles", help="list the outline styles").set_defaults(command=list_styles)
    _add_generate(commands)
    _add_overview(commands)
    _add_docs(commands)
    _add_bundle(commands)
    return parser


def _add_generate(commands) -> None:
    parser = commands.add_parser("generate", help="SVG and STL files per word and colour")
    parser.add_argument("--font", default=_default_font_key(), help="font key, see 'tock-lid fonts'")
    parser.add_argument("--font-file", type=Path, help="any .ttf/.otf/.ttc instead of a built-in font")
    parser.add_argument("--font-index", type=int, default=0, help="face number inside a .ttc file")
    parser.add_argument("--style", default="standard", help="outline style, see 'tock-lid styles'")
    parser.add_argument("--out", type=Path, default=Path("out"))
    _add_shared(parser)
    parser.set_defaults(command=generate)


def _add_overview(commands) -> None:
    parser = commands.add_parser("overview", help="one SVG sheet comparing fonts and styles")
    parser.add_argument("--fonts", nargs="+", default=[_default_font_key()])
    parser.add_argument("--styles", nargs="+", default=list(STYLES))
    parser.add_argument("--out", type=Path, default=Path("out/overview.svg"))
    _add_shared(parser)
    parser.set_defaults(command=overview)


def _add_docs(commands) -> None:
    parser = commands.add_parser("docs", help="the README comparison images")
    parser.add_argument("--out", type=Path, default=Path("docs"), help="output folder")
    _add_shared(parser)
    parser.set_defaults(command=docs)


def _add_bundle(commands) -> None:
    parser = commands.add_parser("bundle", help="a zip with the STLs of every font in every style")
    parser.add_argument("--out", type=Path, default=Path("out/tock-lids.zip"))
    _add_shared(parser)
    parser.set_defaults(command=bundle)


def _add_shared(parser: argparse.ArgumentParser) -> None:
    defaults = LidSpec()
    parser.add_argument("--words", nargs="+", default=DEFAULT_WORDS, help="one lid per word")
    parser.add_argument("--diameter", type=float, default=defaults.diameter_mm, help="lid insert, mm")
    parser.add_argument("--margin", type=float, default=defaults.margin_mm, help="text to edge, mm")
    parser.add_argument(
        "--thickness", type=float, default=defaults.thickness_mm, help="STL depth below z = 0, mm"
    )
