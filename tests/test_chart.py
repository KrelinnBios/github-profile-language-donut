<<<<<<< HEAD
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from language_donut.chart import build_svg, segment_stroke_geometry
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
        self.assertIn('cx="418.0"', svg)
        self.assertIn('cx="26.0"', svg)
        self.assertEqual(5, len(re.findall(r'<text class="label"', svg)))

    def test_eight_languages_use_two_narrow_columns(self):
        totals = Counter({f"Language{i}": 100 - i * 5 for i in range(8)})
        svg = build_svg(totals, config())

        self.assertIn('width="615"', svg)
        self.assertIn('cx="508.0"', svg)
        self.assertEqual(8, len(re.findall(r'<text class="label"', svg)))

    def test_tenth_entry_is_other(self):
        totals = Counter({f"Language{i}": 120 - i * 5 for i in range(12)})
        svg = build_svg(totals, config())

        self.assertEqual(10, len(re.findall(r'<text class="label"', svg)))
        self.assertIn(">Other</text>", svg)
        self.assertNotIn(">Language9</text>", svg)

    def test_tiny_segments_remain_visibly_distinct(self):
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

        self.assertEqual(6, len(re.findall(r'<circle class="segment"', svg)))
        self.assertEqual(3, svg.count('stroke-linecap="butt"'))
        self.assertEqual(3, svg.count('stroke-linecap="round"'))
        expected_colors = (
            "#7F52FF", "#E34F26", "#F7DF1E",
            "#00B8D9", "#22C55E", "#EC4899",
        )
        for color in expected_colors:
            self.assertIn(f'stroke="{color}"', svg)

    def test_round_cap_geometry_stays_inside_segment_bounds(self):
        linecap, dash_length, start_inset = segment_stroke_geometry(
            segment_length=100,
            stroke_width=22,
            gap=3,
            rounded=True,
        )

        self.assertEqual("round", linecap)
        self.assertAlmostEqual(1.5, start_inset - 11)
        self.assertAlmostEqual(98.5, start_inset + dash_length + 11)

    def test_short_segment_falls_back_to_flat_caps(self):
        linecap, dash_length, start_inset = segment_stroke_geometry(
            segment_length=18,
            stroke_width=22,
            gap=3,
            rounded=True,
        )

        self.assertEqual("butt", linecap)
        self.assertAlmostEqual(15, dash_length)
        self.assertAlmostEqual(1.5, start_inset)

    def test_current_language_palette_uses_distinct_colors(self):
        languages = ("Kotlin", "HTML", "JavaScript", "CSS", "Python", "PowerShell")
        colors = {DEFAULT_COLORS[language] for language in languages}

        self.assertEqual(len(languages), len(colors))

    def test_unknown_language_color_is_stable(self):
        first = generated_color("FutureLanguage")
        self.assertEqual(first, generated_color("FutureLanguage"))
        self.assertRegex(first, r"^#[0-9A-F]{6}$")


if __name__ == "__main__":
    unittest.main()
=======
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from language_donut.chart import build_svg, segment_stroke_geometry
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
        self.assertIn('cx="418.0"', svg)
        self.assertIn('cx="26.0"', svg)
        self.assertEqual(5, len(re.findall(r'<text class="label"', svg)))

    def test_eight_languages_use_two_narrow_columns(self):
        totals = Counter({f"Language{i}": 100 - i * 5 for i in range(8)})
        svg = build_svg(totals, config())

        self.assertIn('width="615"', svg)
        self.assertIn('cx="508.0"', svg)
        self.assertEqual(8, len(re.findall(r'<text class="label"', svg)))

    def test_tenth_entry_is_other(self):
        totals = Counter({f"Language{i}": 120 - i * 5 for i in range(12)})
        svg = build_svg(totals, config())

        self.assertEqual(10, len(re.findall(r'<text class="label"', svg)))
        self.assertIn(">Other</text>", svg)
        self.assertNotIn(">Language9</text>", svg)

    def test_tiny_segments_remain_visibly_distinct(self):
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

        self.assertEqual(6, len(re.findall(r'<circle class="segment"', svg)))
        self.assertEqual(3, svg.count('stroke-linecap="butt"'))
        self.assertEqual(3, svg.count('stroke-linecap="round"'))
        expected_colors = (
            "#7F52FF", "#E34F26", "#F7DF1E",
            "#00B8D9", "#22C55E", "#EC4899",
        )
        for color in expected_colors:
            self.assertIn(f'stroke="{color}"', svg)

    def test_round_cap_geometry_stays_inside_segment_bounds(self):
        linecap, dash_length, start_inset = segment_stroke_geometry(
            segment_length=100,
            stroke_width=22,
            gap=3,
            rounded=True,
        )

        self.assertEqual("round", linecap)
        self.assertAlmostEqual(1.5, start_inset - 11)
        self.assertAlmostEqual(98.5, start_inset + dash_length + 11)

    def test_short_segment_falls_back_to_flat_caps(self):
        linecap, dash_length, start_inset = segment_stroke_geometry(
            segment_length=18,
            stroke_width=22,
            gap=3,
            rounded=True,
        )

        self.assertEqual("butt", linecap)
        self.assertAlmostEqual(15, dash_length)
        self.assertAlmostEqual(1.5, start_inset)

    def test_current_language_palette_uses_distinct_colors(self):
        languages = ("Kotlin", "HTML", "JavaScript", "CSS", "Python", "PowerShell")
        colors = {DEFAULT_COLORS[language] for language in languages}

        self.assertEqual(len(languages), len(colors))

    def test_unknown_language_color_is_stable(self):
        first = generated_color("FutureLanguage")
        self.assertEqual(first, generated_color("FutureLanguage"))
        self.assertRegex(first, r"^#[0-9A-F]{6}$")


if __name__ == "__main__":
    unittest.main()
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
