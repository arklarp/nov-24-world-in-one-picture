"""Original editorial vector SVG scene builders and world locator map.

All card canvases use explicit viewBoxes with corner pin safety clear of
[0..25, 0..25] and tagged pill rectangles/labels for automated DOM auditing.
"""

from __future__ import annotations

from html import escape
from typing import Dict, Iterable, Sequence

from data import MAP_PINS, REGION_COLORS, MapPin


def _corner_pin(num: int, color: str) -> str:
    """Top-left circular region-colored story pin, safely inside [2.5..23.5]."""
    return (
        f'<g class="card-pin" data-pin-num="{num}" data-pin-color="{color}">'
        f'<circle cx="13" cy="13" r="9.5" fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>'
        f'<text x="13" y="16.4" text-anchor="middle" fill="#FFFFFF" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="10.2" font-weight="900">{num}</text>'
        f'</g>'
    )


def _pill(
    pill_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    fill: str,
    text_color: str = "#FFFFFF",
    stroke: str | None = None,
    font_size: float = 9.0,
    rx: float = 3.5,
) -> str:
    """Labeled callout pill wired for automated getBBox padding validation."""
    stroke_attr = f' stroke="{stroke}" stroke-width="1.1"' if stroke else ""
    ty = y + h * 0.5 + font_size * 0.35
    tx = x + w * 0.5
    return (
        f'<g class="callout-pill">'
        f'<rect id="{pill_id}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}"{stroke_attr}/>'
        f'<text data-pill-for="{pill_id}" x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
        f'fill="{text_color}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{font_size:.1f}" font-weight="800">{escape(text)}</text>'
        f'</g>'
    )


# ---------------------------------------------------------------------------
# Hero SVG scenes (viewBox 0 0 314 90)
# ---------------------------------------------------------------------------


def _svg_riyadh_tower(num: int, color: str) -> str:
    """#1 Riyadh: Gulf backdrop, Arabian landmass, tower hit, Yemen arc & stacked pills."""
    parts = [
        '<svg viewBox="0 0 314 90" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        # Soft Gulf water backdrop
        '<rect x="0" y="0" width="314" height="90" fill="#DCEEF9"/>',
        # Subtle coastal water bands (solid fills, low PNG entropy)
        '<rect x="0" y="68" width="314" height="22" fill="#CBE5F6"/>',
        # Arabian Peninsula silhouette
        '<path d="M22,12 L132,12 L152,28 L168,46 L154,66 L122,82 L56,82 L32,64 Z" '
        'fill="#F1E3C6" stroke="#B69F78" stroke-width="1.1"/>',
        # Yemen southern region tint
        '<path d="M56,82 L122,82 L134,72 L90,64 L48,68 Z" '
        'fill="#E8CFA0" stroke="#B69F78" stroke-width="0.9"/>',
        # Geography labels
        '<text x="72" y="34" fill="#6B5634" font-family="Arial, Helvetica, sans-serif" '
        'font-size="7.4" font-weight="800">SAUDI ARABIA</text>',
        '<text x="76" y="77" fill="#7C2D12" font-family="Arial, Helvetica, sans-serif" '
        'font-size="7.0" font-weight="800">YEMEN</text>',
        # Riyadh skyline silhouette on mid-right
        '<rect x="164" y="42" width="12" height="44" fill="#334155"/>',
        '<rect x="178" y="22" width="17" height="64" fill="#1E293B"/>',
        '<path d="M180,22 L186.5,11 L193,22 Z" fill="#1E293B"/>',
        '<rect x="183" y="28" width="7" height="8" rx="1" fill="#FDE68A"/>',
        '<rect x="197" y="48" width="11" height="38" fill="#475569"/>',
        # Impact flare & smoke on tower
        '<polygon points="186,25 190,18 193,24 200,23 195,29 198,35 191,32 185,37 186,30 180,28" '
        'fill="#DC2626"/>',
        '<circle cx="190" cy="27" r="3.4" fill="#FACC15"/>',
        '<path d="M192,20 C198,12 206,12 214,8" fill="none" stroke="#64748B" stroke-width="2.6" stroke-linecap="round"/>',
        # Trajectory arc from Yemen toward Riyadh tower (crisp solid vector stroke)
        '<path d="M98,70 Q132,14 182,27" fill="none" stroke="#B91C1C" stroke-width="2.0"/>',
        '<polygon points="183,27 175,23 177,31" fill="#B91C1C"/>',
        '<circle cx="98" cy="70" r="3.2" fill="#B91C1C"/>',
        # Right-stacked callout pills
        _pill("h1-p1", 214, 14, 92, 22, "11 HURT", "#991B1B", "#FFFFFF", font_size=10.5),
        _pill(
            "h1-p2",
            204,
            44,
            102,
            24,
            "SAUDI RETALIATION",
            "#FFFFFF",
            "#9A3412",
            stroke="#B45309",
            font_size=8.4,
        ),
        _corner_pin(num, color),
        "</svg>",
    ]
    return "".join(parts)


def _svg_brooklyn_court(num: int, color: str) -> str:
    """#2 New York: Neoclassical courthouse facade, angled gavel, and stacked pills."""
    parts = [
        '<svg viewBox="0 0 314 90" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="314" height="90" fill="#F5F3FF"/>',
        # Lavender courthouse floor
        '<rect x="0" y="69" width="314" height="21" fill="#EDE9FE"/>',
        '<line x1="0" y1="69" x2="314" y2="69" stroke="#C4B5FD" stroke-width="1"/>',
        # Courthouse pediment and columns
        '<polygon points="34,26 106,9 178,26" fill="#4C1D95"/>',
        '<polygon points="48,24 106,13 164,24" fill="#DDD6FE"/>',
        '<rect x="38" y="26" width="136" height="5" fill="#6D28D9"/>',
        '<rect x="46" y="31" width="11" height="36" fill="#FFFFFF" stroke="#6D28D9" stroke-width="1.2"/>',
        '<rect x="74" y="31" width="11" height="36" fill="#FFFFFF" stroke="#6D28D9" stroke-width="1.2"/>',
        '<rect x="102" y="31" width="11" height="36" fill="#FFFFFF" stroke="#6D28D9" stroke-width="1.2"/>',
        '<rect x="130" y="31" width="11" height="36" fill="#FFFFFF" stroke="#6D28D9" stroke-width="1.2"/>',
        '<rect x="155" y="31" width="11" height="36" fill="#FFFFFF" stroke="#6D28D9" stroke-width="1.2"/>',
        '<rect x="34" y="67" width="144" height="6" fill="#5B21B6"/>',
        '<rect x="28" y="73" width="156" height="5" fill="#7C3AED"/>',
        # Tilted wooden gavel & sound block
        '<rect x="132" y="75" width="44" height="7" rx="2" fill="#78350F"/>',
        '<g transform="translate(152,55) rotate(-32)">'
        '<rect x="-20" y="-4" width="46" height="6.5" rx="2" fill="#92400E"/>'
        '<rect x="-26" y="-12" width="18" height="23" rx="3" fill="#B45309" stroke="#451A03" stroke-width="1.1"/>'
        '<rect x="-23" y="-12" width="3" height="23" fill="#F59E0B"/>'
        '<rect x="-13" y="-12" width="3" height="23" fill="#F59E0B"/>'
        '</g>',
        # Right stacked pills
        _pill("h2-p1", 202, 16, 102, 24, "GUILTY", "#5B21B6", "#FFFFFF", font_size=11.0),
        _pill(
            "h2-p2",
            202,
            47,
            102,
            24,
            "10 OF 12",
            "#FFFFFF",
            "#5B21B6",
            stroke="#6D28D9",
            font_size=10.5,
        ),
        _corner_pin(num, color),
        "</svg>",
    ]
    return "".join(parts)


def _svg_shanghai_probe(num: int, color: str) -> str:
    """#3 Shanghai: Light crimson sky, Pudong skyline + Oriental Pearl, magnifier & pills."""
    parts = [
        '<svg viewBox="0 0 314 90" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="314" height="90" fill="#FEE2E2"/>',
        '<rect x="0" y="72" width="314" height="18" fill="#FECACA"/>',
        # Pudong skyline silhouette
        '<rect x="30" y="42" width="14" height="34" fill="#7F1D1D"/>',
        '<rect x="47" y="28" width="16" height="48" fill="#991B1B"/>',
        '<polygon points="47,28 63,28 59,18 51,18" fill="#991B1B"/>',
        '<rect x="66" y="48" width="12" height="28" fill="#B91C1C"/>',
        # Oriental Pearl spire silhouette
        '<line x1="92" y1="10" x2="92" y2="76" stroke="#7F1D1D" stroke-width="2.4"/>',
        '<line x1="82" y1="76" x2="92" y2="54" stroke="#7F1D1D" stroke-width="2.0"/>',
        '<line x1="102" y1="76" x2="92" y2="54" stroke="#7F1D1D" stroke-width="2.0"/>',
        '<circle cx="92" cy="52" r="7.5" fill="#991B1B"/>',
        '<circle cx="92" cy="30" r="5.2" fill="#B91C1C"/>',
        '<circle cx="92" cy="18" r="2.2" fill="#7F1D1D"/>',
        # Magnifying glass framing executive silhouette with crimson tie
        '<circle cx="144" cy="43" r="24" fill="#FFFFFF" stroke="#991B1B" stroke-width="3.2"/>',
        '<line x1="161" y1="60" x2="177" y2="77" stroke="#7F1D1D" stroke-width="5.2" stroke-linecap="round"/>',
        # Bust silhouette inside lens
        '<circle cx="144" cy="34" r="7.2" fill="#1E293B"/>',
        '<path d="M128,59 C129,47 136,44 144,44 C152,44 159,47 160,59 Z" fill="#1E293B"/>',
        # White collar & red tie
        '<polygon points="141,44 147,44 144,50" fill="#FFFFFF"/>',
        '<polygon points="144,46 146.3,54 144,59 141.7,54" fill="#DC2626"/>',
        # Right stacked pills
        _pill("h3-p1", 196, 16, 108, 24, "UNDER PROBE", "#991B1B", "#FFFFFF", font_size=9.8),
        _pill(
            "h3-p2",
            196,
            47,
            108,
            24,
            "CHEN JINING",
            "#FFFFFF",
            "#991B1B",
            stroke="#B91C1C",
            font_size=9.6,
        ),
        _corner_pin(num, color),
        "</svg>",
    ]
    return "".join(parts)


# ---------------------------------------------------------------------------
# Mid-tier 5x2 SVG scenes (viewBox 0 0 186 50)
# ---------------------------------------------------------------------------


def _svg_ukraine_raids(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#1E293B"/>',
        '<rect x="0" y="34" width="186" height="16" fill="#0F172A"/>',
        # Skyline blocks
        '<rect x="28" y="25" width="14" height="23" fill="#334155"/>',
        '<rect x="45" y="18" width="16" height="30" fill="#475569"/>',
        '<rect x="64" y="27" width="15" height="21" fill="#334155"/>',
        '<rect x="83" y="22" width="14" height="26" fill="#475569"/>',
        # Smoke plume and blast star
        '<path d="M54,18 C60,10 68,11 76,6" fill="none" stroke="#94A3B8" stroke-width="2.6" stroke-linecap="round"/>',
        '<polygon points="52,19 56,12 59,18 65,18 60,22 62,27 56,24 51,27 52,22 47,19" fill="#EF4444"/>',
        '<circle cx="56" cy="20" r="2.6" fill="#FDE047"/>',
        _pill("m4-p1", 110, 7, 70, 17, "9 KILLED", "#B91C1C", "#FFFFFF", font_size=9.0),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_sanofi_deal(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#EFF6FF"/>',
        # Capsule pill
        '<g transform="translate(50,27) rotate(-26)">'
        '<rect x="-20" y="-7" width="20" height="14" rx="7" fill="#1E3A8A"/>'
        '<rect x="-6" y="-7" width="26" height="14" rx="7" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="1.4"/>'
        '<rect x="-20" y="-7" width="20" height="14" rx="7" fill="#1E3A8A"/>'
        '</g>',
        # Lab Erlenmeyer flask
        '<path d="M84,12 L94,12 L94,20 L103,40 C104,42 103,44 100,44 L78,44 C75,44 74,42 75,40 L84,20 Z" '
        'fill="#FFFFFF" stroke="#1E3A8A" stroke-width="1.6"/>',
        '<path d="M80,33 L98,33 L102,42 L76,42 Z" fill="#3B82F6"/>',
        '<circle cx="87" cy="38" r="1.5" fill="#EFF6FF"/>',
        '<circle cx="92" cy="36" r="1.2" fill="#EFF6FF"/>',
        _pill("m5-p1", 114, 7, 66, 17, "$41BN", "#1E3A8A", "#FFFFFF", font_size=9.4),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_dow_record(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#0F172A"/>',
        # Subtle chart guide lines
        '<line x1="26" y1="38" x2="96" y2="38" stroke="#334155" stroke-width="0.9"/>',
        '<line x1="26" y1="26" x2="96" y2="26" stroke="#334155" stroke-width="0.9"/>',
        '<line x1="26" y1="14" x2="96" y2="14" stroke="#334155" stroke-width="0.9"/>',
        # Rising green bars
        '<rect x="30" y="33" width="9" height="12" fill="#16A34A"/>',
        '<rect x="43" y="29" width="9" height="16" fill="#22C55E"/>',
        '<rect x="56" y="24" width="9" height="21" fill="#22C55E"/>',
        '<rect x="69" y="18" width="9" height="27" fill="#4ADE80"/>',
        '<rect x="82" y="11" width="9" height="34" fill="#86EFAC"/>',
        '<polyline points="34,31 47,26 60,21 73,15 86,9" fill="none" stroke="#FACC15" stroke-width="1.8"/>',
        _pill("m6-p1", 98, 6, 82, 16, "DOW 50,018", "#15803D", "#FFFFFF", font_size=8.6),
        _pill("m6-p2", 98, 26, 82, 16, "NASDAQ -1.5%", "#991B1B", "#FFFFFF", font_size=8.0),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_ariane_launch(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#0F172A"/>',
        # Starfield dots
        '<circle cx="40" cy="12" r="1.1" fill="#E2E8F0"/>',
        '<circle cx="76" cy="9" r="1.2" fill="#E2E8F0"/>',
        '<circle cx="96" cy="24" r="1.0" fill="#94A3B8"/>',
        '<circle cx="152" cy="36" r="1.1" fill="#E2E8F0"/>',
        # Orbital arc + miniature satellite icons
        '<path d="M28,44 Q92,8 176,34" fill="none" stroke="#38BDF8" stroke-width="1.1"/>',
        '<rect x="86" y="18" width="6" height="3" fill="#38BDF8"/>',
        '<rect x="102" y="22" width="6" height="3" fill="#38BDF8"/>',
        '<rect x="122" y="29" width="6" height="3" fill="#38BDF8"/>',
        # Ariane 6 rocket rising
        '<g transform="translate(56,28) rotate(22)">'
        '<polygon points="0,-16 4,-8 -4,-8" fill="#F8FAFC"/>'
        '<rect x="-4" y="-8" width="8" height="20" fill="#E2E8F0"/>'
        '<rect x="-7.5" y="0" width="3" height="12" fill="#94A3B8"/>'
        '<rect x="4.5" y="0" width="3" height="12" fill="#94A3B8"/>'
        '<polygon points="-3,12 3,12 0,21" fill="#F97316"/>'
        '</g>',
        _pill("m7-p1", 112, 7, 68, 17, "36 SATS", "#334155", "#FFFFFF", stroke="#64748B", font_size=8.8),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_uae_bus(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#FFF7ED"/>',
        # Highway tarmac
        '<rect x="0" y="34" width="186" height="16" fill="#475569"/>',
        '<rect x="12" y="41" width="18" height="2.2" fill="#FDE047"/>',
        '<rect x="44" y="41" width="18" height="2.2" fill="#FDE047"/>',
        '<rect x="76" y="41" width="18" height="2.2" fill="#FDE047"/>',
        '<rect x="108" y="41" width="18" height="2.2" fill="#FDE047"/>',
        '<rect x="140" y="41" width="18" height="2.2" fill="#FDE047"/>',
        # Worker bus
        '<rect x="28" y="21" width="44" height="15" rx="2" fill="#EA580C"/>',
        '<rect x="33" y="24" width="8" height="5" fill="#FED7AA"/>',
        '<rect x="44" y="24" width="8" height="5" fill="#FED7AA"/>',
        '<rect x="55" y="24" width="12" height="5" fill="#FED7AA"/>',
        '<circle cx="38" cy="36" r="3.4" fill="#0F172A"/>',
        '<circle cx="62" cy="36" r="3.4" fill="#0F172A"/>',
        # Stalled truck ahead
        '<rect x="82" y="18" width="28" height="18" fill="#64748B"/>',
        '<rect x="110" y="24" width="12" height="12" fill="#334155"/>',
        '<circle cx="91" cy="36" r="3.4" fill="#0F172A"/>',
        '<circle cx="115" cy="36" r="3.4" fill="#0F172A"/>',
        # Impact warning star
        '<polygon points="77,20 80,25 85,25 81,28 82,33 77,30 72,33 73,28 69,25 74,25" fill="#DC2626"/>',
        _pill("m8-p1", 112, 6, 68, 17, "13 DEAD", "#C2410C", "#FFFFFF", font_size=9.0),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_sudan_water(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#ECFDF5"/>',
        # Soft hills
        '<path d="M0,42 Q42,26 96,38 T186,34 L186,50 L0,50 Z" fill="#BBF7D0"/>',
        '<path d="M0,45 Q65,33 130,43 L186,40 L186,50 L0,50 Z" fill="#86EFAC"/>',
        # Clean water drop emblem + ripples
        '<path d="M64,9 C64,9 51,24 51,31 C51,38 56.8,43 64,43 C71.2,43 77,38 77,31 C77,24 64,9 64,9 Z" '
        'fill="#0284C7" stroke="#0369A1" stroke-width="1.3"/>',
        '<path d="M58,28 C57,33 59,37 63,38" fill="none" stroke="#BAE6FD" stroke-width="1.8" stroke-linecap="round"/>',
        '<ellipse cx="64" cy="45" rx="22" ry="3.2" fill="none" stroke="#0284C7" stroke-width="1.1"/>',
        _pill("m9-p1", 108, 7, 72, 17, "$55M AID", "#15803D", "#FFFFFF", font_size=8.9),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_hanoi_blast(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#F0FDFA"/>',
        '<rect x="0" y="40" width="186" height="10" fill="#CBD5E1"/>',
        # Shopfront silhouette
        '<rect x="34" y="18" width="54" height="24" fill="#115E59"/>',
        '<rect x="31" y="15" width="60" height="5" fill="#0F766E"/>',
        '<rect x="40" y="25" width="14" height="17" fill="#CCFBF1"/>',
        '<rect x="59" y="25" width="22" height="10" fill="#99F6E4"/>',
        # Blast burst star
        '<polygon points="78,10 83,18 93,16 88,24 96,30 85,31 82,39 76,32 67,34 71,26 65,19 74,19" '
        'fill="#EA580C"/>',
        '<polygon points="78,16 81,21 87,21 83,25 85,30 79,28 74,30 75,25 71,21 76,21" '
        'fill="#FACC15"/>',
        _pill("m10-p1", 114, 7, 66, 17, "6 DEAD", "#0F766E", "#FFFFFF", font_size=9.1),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_nepal_quake(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#FEFCE8"/>',
        # Clean seismic grid (solid thin strokes)
        '<line x1="26" y1="15" x2="180" y2="15" stroke="#E5DEC9" stroke-width="0.8"/>',
        '<line x1="26" y1="26" x2="180" y2="26" stroke="#D6CCB0" stroke-width="0.9"/>',
        '<line x1="26" y1="37" x2="180" y2="37" stroke="#E5DEC9" stroke-width="0.8"/>',
        '<line x1="56" y1="6" x2="56" y2="46" stroke="#E5DEC9" stroke-width="0.8"/>',
        '<line x1="92" y1="6" x2="92" y2="46" stroke="#E5DEC9" stroke-width="0.8"/>',
        '<line x1="128" y1="6" x2="128" y2="46" stroke="#E5DEC9" stroke-width="0.8"/>',
        # High-amplitude seismograph waveform
        '<polyline points="26,26 42,26 48,22 54,30 60,18 66,36 72,8 78,44 84,12 90,39 96,19 102,32 108,24 116,28 126,26 178,26" '
        'fill="none" stroke="#B45309" stroke-width="2.0" stroke-linejoin="round"/>',
        _pill("m11-p1", 118, 7, 62, 17, "M5.3", "#B45309", "#FFFFFF", font_size=9.6),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_brazil_floods(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#FDF2F8"/>',
        # Flood water waves at bottom
        '<path d="M0,38 Q22,33 44,38 T88,38 T132,38 T186,38 L186,50 L0,50 Z" fill="#3B82F6"/>',
        '<path d="M0,43 Q24,39 48,43 T96,43 T144,43 T186,43 L186,50 L0,50 Z" fill="#1D4ED8"/>',
        # Storm clouds
        '<circle cx="46" cy="18" r="9" fill="#475569"/>',
        '<circle cx="59" cy="15" r="11" fill="#334155"/>',
        '<circle cx="74" cy="18" r="9" fill="#475569"/>',
        '<rect x="44" y="18" width="32" height="9" fill="#475569"/>',
        # Lightning bolt + rain streaks
        '<polygon points="62,21 56,31 62,31 58,40 69,28 63,28 67,21" fill="#FACC15"/>',
        '<line x1="42" y1="29" x2="38" y2="37" stroke="#2563EB" stroke-width="1.6"/>',
        '<line x1="50" y1="29" x2="46" y2="37" stroke="#2563EB" stroke-width="1.6"/>',
        '<line x1="76" y1="29" x2="72" y2="37" stroke="#2563EB" stroke-width="1.6"/>',
        '<line x1="84" y1="29" x2="80" y2="37" stroke="#2563EB" stroke-width="1.6"/>',
        _pill("m12-p1", 108, 7, 72, 17, "20K FLEE", "#BE185D", "#FFFFFF", font_size=8.9),
        _corner_pin(num, color),
        "</svg>",
    ])


def _svg_australia_law(num: int, color: str) -> str:
    return "".join([
        '<svg viewBox="0 0 186 50" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="186" height="50" fill="#F0F9FF"/>',
        # Circuit traces
        '<polyline points="26,20 44,20 50,14" fill="none" stroke="#7DD3FC" stroke-width="1.5"/>',
        '<circle cx="50" cy="14" r="2.2" fill="#0284C7"/>',
        '<polyline points="26,34 42,34 48,40" fill="none" stroke="#7DD3FC" stroke-width="1.5"/>',
        '<circle cx="48" cy="40" r="2.2" fill="#0284C7"/>',
        '<polyline points="86,34 108,34 114,40 166,40" fill="none" stroke="#7DD3FC" stroke-width="1.5"/>',
        '<circle cx="166" cy="40" r="2.2" fill="#0284C7"/>',
        # Shield with checkmark emblem
        '<path d="M68,9 L84,14 L84,26 C84,35 76,41 68,44 C60,41 52,35 52,26 L52,14 Z" '
        'fill="#0284C7" stroke="#0369A1" stroke-width="1.5"/>',
        '<polyline points="60,26 66,32 76,20" fill="none" stroke="#FFFFFF" '
        'stroke-width="3.0" stroke-linecap="round" stroke-linejoin="round"/>',
        _pill("m13-p1", 112, 7, 68, 17, "5% FINE", "#0284C7", "#FFFFFF", font_size=9.1),
        _corner_pin(num, color),
        "</svg>",
    ])


SCENE_BUILDERS = {
    "riyadh_tower": _svg_riyadh_tower,
    "brooklyn_court": _svg_brooklyn_court,
    "shanghai_probe": _svg_shanghai_probe,
    "ukraine_raids": _svg_ukraine_raids,
    "sanofi_deal": _svg_sanofi_deal,
    "dow_record": _svg_dow_record,
    "ariane_launch": _svg_ariane_launch,
    "uae_bus": _svg_uae_bus,
    "sudan_water": _svg_sudan_water,
    "hanoi_blast": _svg_hanoi_blast,
    "nepal_quake": _svg_nepal_quake,
    "brazil_floods": _svg_brazil_floods,
    "australia_law": _svg_australia_law,
}


def build_card_svg(scene_key: str, story_id: int, region: str) -> str:
    """Return the custom SVG markup for an illustrated card."""
    builder = SCENE_BUILDERS[scene_key]
    return builder(story_id, REGION_COLORS[region])


def build_world_map_svg(pins: Sequence[MapPin] = MAP_PINS) -> str:
    """Build the 360x185 world locator SVG with crisp solid lines and 13 pins."""
    parts = [
        '<svg viewBox="0 0 360 185" xmlns="http://www.w3.org/2000/svg">',
        # Ice-blue ocean
        '<rect x="0" y="0" width="360" height="185" fill="#E6F2FA"/>',
        # Clean solid faint graticule grid (zero dasharray to keep PNG compact)
        '<g stroke="#CDE0EE" stroke-width="0.7">',
        '<line x1="0" y1="46" x2="360" y2="46"/>',
        '<line x1="0" y1="92" x2="360" y2="92"/>',
        '<line x1="0" y1="138" x2="360" y2="138"/>',
        '<line x1="60" y1="0" x2="60" y2="185"/>',
        '<line x1="120" y1="0" x2="120" y2="185"/>',
        '<line x1="180" y1="0" x2="180" y2="185"/>',
        '<line x1="240" y1="0" x2="240" y2="185"/>',
        '<line x1="300" y1="0" x2="300" y2="185"/>',
        "</g>",
        # Original stylized olive-slate continent polygons
        '<g fill="#94A396" stroke="#3F4D42" stroke-width="0.9" stroke-linejoin="round">',
        # North America
        '<path d="M18,34 L42,24 L76,22 L104,34 L112,50 L98,66 L86,78 L72,88 L64,96 '
        'L55,86 L46,74 L32,60 L20,46 Z"/>',
        # Greenland
        '<path d="M114,14 L138,12 L144,24 L130,36 L116,28 Z"/>',
        # South America
        '<path d="M98,96 L118,96 L136,108 L146,124 L136,144 L122,164 L108,176 '
        'L101,158 L98,134 L90,114 Z"/>',
        # Europe
        '<path d="M164,58 L166,42 L180,30 L196,24 L216,28 L224,42 L214,56 '
        'L198,60 L182,62 L170,62 Z"/>',
        # UK & Ireland
        '<path d="M162,40 L169,38 L170,48 L163,49 Z"/>',
        # Africa
        '<path d="M164,68 L188,65 L208,74 L218,92 L226,106 L214,126 L204,148 '
        'L192,158 L182,140 L176,118 L160,96 L158,78 Z"/>',
        # Madagascar
        '<path d="M223,132 L228,132 L226,146 L221,144 Z"/>',
        # Asia + Arabian Peninsula + India + SE Asia
        '<path d="M214,56 L224,42 L240,24 L278,20 L318,28 L336,42 L322,58 '
        'L312,74 L298,88 L294,104 L282,108 L276,94 L268,98 L258,104 L248,94 '
        'L234,98 L222,94 L214,76 L218,64 Z"/>',
        # Japan
        '<path d="M326,56 L333,52 L334,66 L327,70 Z"/>',
        # Maritime SE Asia (Sumatra/Java/Borneo/Philippines)
        '<path d="M282,113 L294,114 L304,119 L294,123 L282,118 Z"/>',
        '<path d="M300,104 L310,106 L312,115 L302,114 Z"/>',
        '<path d="M312,92 L318,94 L317,104 L312,102 Z"/>',
        # New Guinea
        '<path d="M320,114 L336,116 L338,122 L322,120 Z"/>',
        # Australia
        '<path d="M294,132 L318,128 L336,138 L334,158 L314,164 L296,154 L290,142 Z"/>',
        # New Zealand
        '<path d="M344,160 L351,156 L352,168 L345,172 Z"/>',
        "</g>",
    ]

    # Plot Pins 1..13 in order
    for pin in pins:
        fill = REGION_COLORS[pin.region]
        parts.append(
            f'<g class="map-pin" data-pin-num="{pin.story_id}" data-pin-color="{fill}">'
            f'<circle cx="{pin.x:.1f}" cy="{pin.y:.1f}" r="8.2" '
            f'fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>'
            f'<text x="{pin.x:.1f}" y="{pin.y + 3.1:.1f}" text-anchor="middle" fill="#FFFFFF" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="8.8" font-weight="900">'
            f'{pin.story_id}</text>'
            f'</g>'
        )

    parts.append("</svg>")
    return "".join(parts)
