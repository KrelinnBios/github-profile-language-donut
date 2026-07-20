import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from language_donut.chart import build_svg
from language_donut.colors import generated_color
from language_donut.config import DEFAULT_CHART, DEFAULT_COLORS, DEFAULT_THEME


def config():
    return {
        "max_languages": 9,
        "chart": DEFAULT_CHART.copy(),
        "theme": DEFAULT_THEME.copy(),
        "colors": DEFAULT_COLORS.copy(),
    }


class BuildSvgTests(unittest.TestCase):

    def test_five_languages_use_one_column(self):
        totals = Counter({f"Language{i}": 100 - i * 10 for i in range(5)})
        svg = build_svg(totals, config())

        self.assertIn('width="525"', svg)
        self.assertIn('class="center-value" x="418.0"', svg)
        self.assertIn('cx="26.0"', svg)
        self.assertEqual(5, len(re.findall(r'<text class="label"', svg)))

    def test_eight_languages_use_two_columns(self):
        totals = Counter({f"Language{i}": 100 - i * 5 for i in range(8)})
        svg = build_svg(totals, config())

        self.assertIn('width="615"', svg)
        self.assertIn('class="center-value" x="508.0"', svg)
        self.assertEqual(8, len(re.findall(r'<text class="label"', svg)))

    def test_tenth_entry_is_other(self):
        totals = Counter({f"Language{i}": 120 - i * 5 for i in range(12)})
        svg = build_svg(totals, config())

        self.assertEqual(10, len(re.findall(r'<text class="label"', svg)))
        self.assertIn(">Other</text>", svg)
        self.assertNotIn(">Language9</text>", svg)

    def test_segments_render_as_contiguous_annular_paths(self):
        totals = Counter(
            {
                "Kotlin": 4500,
                "HTML": 3400,
                "JavaScript": 1800,
                "CSS": 320,
                "Python": 40,
                "PowerShell": 20,
            }
        )
        svg = build_svg(totals, config())

        self.assertEqual(6, len(re.findall(r'<path class="segment"', svg)))
        self.assertIn('class="donut-track" d="M', svg)
        self.assertIn(" Q ", svg)
        self.assertIn("A 72.00 72.00", svg)
        self.assertIn("A 50.00 50.00", svg)
        self.assertNotIn("stroke-linecap: round;", svg)
        self.assertNotIn("stroke-dasharray", svg)

        for color in (
            "#7F52FF",
            "#E34F26",
            "#F7DF1E",
            "#00B8D9",
            "#22C55E",
            "#EC4899",
        ):
            self.assertIn(f'fill="{color}"', svg)

    def test_tiny_segments_remain_on_the_donut(self):
        totals = Counter(
            {
                "Kotlin": 9000,
                "Python": 10,
                "PowerShell": 5,
            }
        )
        svg = build_svg(totals, config())

        self.assertEqual(3, len(re.findall(r'<path class="segment"', svg)))
        for color in ("#7F52FF", "#22C55E", "#EC4899"):
            self.assertIn(f'fill="{color}"', svg)

    def test_current_language_palette_uses_distinct_colors(self):
        languages = (
            "Kotlin",
            "HTML",
            "JavaScript",
            "CSS",
            "Python",
            "PowerShell",
        )
        colors = {DEFAULT_COLORS[language] for language in languages}
        self.assertEqual(len(languages), len(colors))

    def test_unknown_language_color_is_stable(self):
        first = generated_color("FutureLanguage")
        second = generated_color("FutureLanguage")

        self.assertEqual(first, second)
        self.assertRegex(first, r"^#[0-9A-F]{6}$")


if __name__ == "__main__":
    unittest.main()
