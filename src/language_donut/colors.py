import colorsys
import hashlib


def displayed_languages(totals, max_named_languages):
    items = totals.most_common()
    if max_named_languages <= 0 or len(items) <= max_named_languages:
        return items
    visible = items[:max_named_languages]
    visible.append(("Other", sum(value for _, value in items[max_named_languages:])))
    return visible


def generated_color(language):
    digest = hashlib.sha256(language.encode("utf-8")).digest()
    hue = int.from_bytes(digest[:2], "big") / 65535
    red, green, blue = colorsys.hls_to_rgb(hue, 0.55, 0.72)
    return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"


def color_for(language, colors):
    return colors.get(language, generated_color(language))


def percentage_label(value):
    return f"{value:.1f}%"
