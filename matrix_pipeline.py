import subprocess

import louis


def convert_braille_cell_to_dot_list(cell_char: str) -> list[int]:
    codepoint = ord(cell_char)
    dot_mask = codepoint - 0x2800
    return [(dot_mask >> i) & 1 for i in range(6)]


def convert_braille_string_to_dot_lists(braille_text: str) -> list[list[int]]:
    return [convert_braille_cell_to_dot_list(cell) for cell in braille_text]


def generate_braille_model_from_text(
        text: str,
        output_path: str = "models/braille_model.stl",
        dot_radius: float | None = None,
        dot_spacing: float | None = None,
        row_spacing: float | None = None,
        column_spacing: float | None = None,
        page_thickness: float | None = None,
        max_page_width: float | None = None,
        gen_timeout_seconds: float | None = None,
) -> None:
    tables = ["braille-patterns.cti", "en-us-g2.ctb"]
    braille_text = louis.translateString(tables, text)
    dot_lists = convert_braille_string_to_dot_lists(braille_text)
    openscad_dot_lists = str(dot_lists).replace(" ", "")

    openscad_args = ["openscad", "-o", output_path, "-D", f"chars={openscad_dot_lists}"]

    if dot_radius is not None:
        openscad_args.extend(["-D", f"DOT_RADIUS={dot_radius}"])
    if dot_spacing is not None:
        openscad_args.extend(["-D", f"DOT_SPACING={dot_spacing}"])
    if row_spacing is not None:
        openscad_args.extend(["-D", f"ROW_SPACING={row_spacing}"])
    if column_spacing is not None:
        openscad_args.extend(["-D", f"COLUMN_SPACING={column_spacing}"])
    if page_thickness is not None:
        openscad_args.extend(["-D", f"PAGE_THICKNESS={page_thickness}"])
    if max_page_width is not None:
        openscad_args.extend(["-D", f"MAX_PAGE_WIDTH={max_page_width}"])

    openscad_args.append("matrix_generator.scad")

    subprocess.run(openscad_args, capture_output=True, text=True, timeout=gen_timeout_seconds)
