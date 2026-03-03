import subprocess

import louis


def convert_braille_cell_to_dot_list(cell_char: str) -> list[int]:
    codepoint = ord(cell_char)
    dot_mask = codepoint - 0x2800
    return [(dot_mask >> i) & 1 for i in range(6)]


def convert_braille_string_to_dot_lists(braille_text: str) -> list[list[int]]:
    return [convert_braille_cell_to_dot_list(cell) for cell in braille_text]


def generate_braille_model_from_text(text: str) -> None:
    tables = ["braille-patterns.cti", "en-us-g2.ctb"]
    braille_text = louis.translateString(tables, text)
    dot_lists = convert_braille_string_to_dot_lists(braille_text)
    openscad_dot_lists = str(dot_lists).replace(" ", "")
    subprocess.run(
        ["openscad", "-o", "models/braille_model.stl", "-D", f"chars={openscad_dot_lists}", "matrix_generator.scad"],
        capture_output=True,
        text=True
    )


if __name__ == "__main__":
    generate_braille_model_from_text(input("Enter text to convert to braille model: "))
