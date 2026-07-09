import matrix_pipeline


def test_translate_text_to_braille_text_returns_braille_text_for_string_abc():
    assert matrix_pipeline.translate_text_to_braille_text("abc") == "⠁⠃⠉"


def test_convert_braille_cell_to_dot_list_returns_dot_list_for_letter_a():
    assert matrix_pipeline.convert_braille_cell_to_dot_list("⠁") == [1, 0, 0, 0, 0, 0]


def test_convert_braille_cell_to_dot_list_returns_dot_list_for_letter_b():
    assert matrix_pipeline.convert_braille_cell_to_dot_list("⠃") == [1, 1, 0, 0, 0, 0]


def test_convert_braille_cell_to_dot_list_returns_dot_list_for_letter_c():
    assert matrix_pipeline.convert_braille_cell_to_dot_list("⠉") == [1, 0, 0, 1, 0, 0]


def test_convert_braille_string_to_dot_lists_returns_dot_list_for_string_abc():
    assert matrix_pipeline.convert_braille_string_to_dot_lists("abc") == [
        [1, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 1]
    ]


def test_generate_braille_model_from_text_creates_non_empty_stl(tmp_path):
    output_path = tmp_path / "abc.stl"

    matrix_pipeline.generate_braille_model_from_text(
        text="abc",
        output_path=str(output_path)
    )

    assert output_path.is_file()
    assert output_path.stat().st_size > 0
