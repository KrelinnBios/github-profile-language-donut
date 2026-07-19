<<<<<<< HEAD
#!/usr/bin/env python3
"""Generate a versioned SVG language donut chart for a GitHub profile."""

import argparse
from pathlib import Path

from language_donut.chart import build_svg
from language_donut.config import load_config
from language_donut.github import language_totals, repository_context
from language_donut.output import set_action_outputs, write_outputs


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="language-donut.config.json")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--output-directory", default=".")
    parser.add_argument("--output-prefix", default="language-donut")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(Path(args.config))
    owner, profile_repository = repository_context(config)
    totals = language_totals(owner, profile_repository, config)
    image, changed = write_outputs(
        build_svg(totals, config),
        Path(args.readme),
        Path(args.output_directory),
        args.output_prefix,
    )
    set_action_outputs(image, changed)
    print(f"已生成 {image.as_posix()}（{'有变更' if changed else '无变更'}）")


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
"""Generate a versioned SVG language donut chart for a GitHub profile."""

import argparse
from pathlib import Path

from language_donut.chart import build_svg
from language_donut.config import load_config
from language_donut.github import language_totals, repository_context
from language_donut.output import set_action_outputs, write_outputs


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="language-donut.config.json")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--output-directory", default=".")
    parser.add_argument("--output-prefix", default="language-donut")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(Path(args.config))
    owner, profile_repository = repository_context(config)
    totals = language_totals(owner, profile_repository, config)
    image, changed = write_outputs(
        build_svg(totals, config),
        Path(args.readme),
        Path(args.output_directory),
        args.output_prefix,
    )
    set_action_outputs(image, changed)
    print(f"已生成 {image.as_posix()}（{'有变更' if changed else '无变更'}）")


if __name__ == "__main__":
    main()
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
