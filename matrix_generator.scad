$fn = 7;

DOT_RADIUS = 1;
DOT_SPACING = 2.5;
ROW_SPACING = 3.75 + DOT_SPACING;
COLUMN_SPACING = 10.25;
PAGE_THICKNESS = 2;
MAX_PAGE_WIDTH = 200;
MAX_CHARS_PER_LINE = floor(MAX_PAGE_WIDTH / ROW_SPACING);

module render_braille_cell(dot_pattern) {
  ROW_COUNT = 2;
  COL_COUNT = 3;
  TOTAL_DOTS = ROW_COUNT * COL_COUNT;

  function dot_x(index) = (index % COL_COUNT) * DOT_SPACING + DOT_SPACING;
  function dot_y(index) = floor(index / COL_COUNT) * DOT_SPACING + (ROW_SPACING - DOT_SPACING) / 2;

  for (index = [0:TOTAL_DOTS - 1]) {
    if (dot_pattern[index] != 0) {
      union() {
        color([1, 1, 1])
          translate(v=[dot_x(index), dot_y(index), 0]) {
            intersection() {
              sphere(DOT_RADIUS * dot_pattern[index]);
              translate([0, 0, DOT_RADIUS / 2 - 0.01])
                cube(size=[2, 2, DOT_RADIUS], center=true);
            }
          }
      }
    }
  }
}

module render_braille_group(chars, total_chars) {
  union() {
    for (char_index = [0:total_chars - 1]) {
      translate(v=[0, char_index * ROW_SPACING, PAGE_THICKNESS]) {
        current_char = chars[char_index];
        if (current_char != undef) {
          render_braille_cell(chars[char_index]);
        } else {
          render_braille_cell([0, 0, 0, 0, 0, 0]);
        }
      }
    }
    translate(v=[0, -ROW_SPACING / 2, 0]) {
      color([0.2, 0.2, 0.2]) {
        cube(size=[COLUMN_SPACING, ROW_SPACING * (total_chars + 1), PAGE_THICKNESS]);
        linear_extrude(PAGE_THICKNESS)
          polygon(
            points=[
              [0, ROW_SPACING * (total_chars + 1)],
              [COLUMN_SPACING, ROW_SPACING * (total_chars + 1)],
            ]
          );
      }
    }
  }
}

union() {
  total_chars = len(chars);
  chars_per_group = min(len(chars), MAX_CHARS_PER_LINE);

  for (group_index = [0:floor((total_chars - 1) / chars_per_group)]) {
    start_index = group_index * chars_per_group;
    end_index = min(start_index + chars_per_group - 1, total_chars - 1);

    char_group = [
      for (char_index = [start_index:end_index]) chars[char_index],
    ];

    translate([group_index * COLUMN_SPACING, 0, 0])
      render_braille_group(char_group, chars_per_group);
  }
}
