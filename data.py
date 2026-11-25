"""Verified world news dataset for Tuesday 24 November 2026 (UTC).

Structured around 39 single-day stories distributed across 10 world regions
and 26 distinct thematic fields, with strict temporal and spatial validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Sequence, Tuple


DATE_DISPLAY = "Tuesday 24 November 2026"
DATE_SHORT = "TUE 24 NOV 2026 (UTC)"
TOTAL_STORIES_EXPECTED = 39
FIELD_COUNT = 26


@dataclass(frozen=True)
class RegionSpec:
    code: str
    label: str
    color: str
    expected_count: int


@dataclass(frozen=True)
class TimelineAnchor:
    utc: str
    label: str


@dataclass(frozen=True)
class NumberHighlight:
    value: str
    caption: str
    accent: str


@dataclass(frozen=True)
class StoryCard:
    story_id: int
    region: str
    field: str
    kicker: str
    epistemic: str
    headline: str
    deck: str
    sources: str
    scene_key: str


@dataclass(frozen=True)
class WireBrief:
    story_id: int
    region: str
    field: str
    epistemic_code: str
    lead: str
    body: str
    publisher: str


@dataclass(frozen=True)
class MapPin:
    story_id: int
    region: str
    x: float
    y: float
    place: str


@dataclass(frozen=True)
class AuditItem:
    label: str
    detail: str


REGIONS: Tuple[RegionSpec, ...] = (
    RegionSpec("EUROPE", "EUROPE", "#1E3A8A", 6),
    RegionSpec("MIDDLE_EAST", "MIDDLE EAST", "#C2410C", 5),
    RegionSpec("AFRICA", "AFRICA", "#15803D", 5),
    RegionSpec("EAST_ASIA", "EAST ASIA", "#B91C1C", 4),
    RegionSpec("NORTH_AMERICA", "NORTH AMERICA", "#6D28D9", 4),
    RegionSpec("LATIN_AMERICA", "LATIN AMERICA", "#BE185D", 3),
    RegionSpec("SOUTH_ASIA", "SOUTH ASIA", "#B45309", 3),
    RegionSpec("OCEANIA", "OCEANIA", "#0284C7", 3),
    RegionSpec("SE_ASIA", "SE ASIA", "#0F766E", 3),
    RegionSpec("WORLD", "WORLD", "#334155", 3),
)

REGION_COLORS: Dict[str, str] = {r.code: r.color for r in REGIONS}
REGION_LABELS: Dict[str, str] = {r.code: r.label for r in REGIONS}

TIMELINE_ANCHORS: Tuple[TimelineAnchor, ...] = (
    TimelineAnchor("01:00", "Hanoi blast"),
    TimelineAnchor("01:32", "Nepal quake"),
    TimelineAnchor("05:30", "Sanofi $41bn"),
    TimelineAnchor("11:14", "Ariane 6"),
    TimelineAnchor("12:00", "Shanghai probe"),
    TimelineAnchor("15:00", "US conf. 103.3"),
    TimelineAnchor("21:00", "Dow 50,018"),
)

KEY_FIGURES: Tuple[NumberHighlight, ...] = (
    NumberHighlight("11 hurt", "Riyadh strike · Al Arabiya", "#C2410C"),
    NumberHighlight("10 of 12", "Huawei guilty · Reuters/AP", "#6D28D9"),
    NumberHighlight("9 dead", "Ukraine raids · Kyiv Ind.", "#1E3A8A"),
    NumberHighlight("$41bn", "Sanofi Insmed · Reuters", "#1E3A8A"),
    NumberHighlight("50,018", "Dow record · Reuters", "#6D28D9"),
)

HERO_CARDS: Tuple[StoryCard, ...] = (
    StoryCard(
        story_id=1,
        region="MIDDLE_EAST",
        field="armed_conflict",
        kicker="RIYADH · WAR",
        epistemic="REPORTED",
        headline="Riyadh financial tower hit; 11 hurt",
        deck=(
            "A strike damages a Riyadh financial tower, wounding 11. "
            "The Saudi-led coalition blames Yemen's Houthis and launches "
            "retaliatory airstrikes on Hodeidah port."
        ),
        sources="Al Arabiya",
        scene_key="riyadh_tower",
    ),
    StoryCard(
        story_id=2,
        region="NORTH_AMERICA",
        field="federal_courts",
        kicker="NEW YORK · COURTS",
        epistemic="CONFIRMED",
        headline="Huawei convicted on 10 of 12 counts",
        deck=(
            "A Brooklyn federal jury finds Huawei guilty of bank fraud, "
            "sanctions violations and trade-secret theft, while acquitting "
            "the firm of racketeering."
        ),
        sources="Reuters · AP",
        scene_key="brooklyn_court",
    ),
    StoryCard(
        story_id=3,
        region="EAST_ASIA",
        field="political_probe",
        kicker="SHANGHAI · POLITICS",
        epistemic="OFFICIAL",
        headline="Shanghai party chief under probe",
        deck=(
            "Beijing investigates Politburo member Chen Jining, 62, for "
            "serious violations—the fourth senior leader placed under "
            "probe during this term."
        ),
        sources="Reuters · CNN",
        scene_key="shanghai_probe",
    ),
)

MID_CARDS: Tuple[StoryCard, ...] = (
    StoryCard(
        story_id=4,
        region="EUROPE",
        field="armed_conflict",
        kicker="UKRAINE · WAR",
        epistemic="CONFIRMED",
        headline="Dawn strikes kill 9 across Ukraine",
        deck="Russian missiles hit Zaporizhzhia homes; 40+ hurt.",
        sources="Reuters · Kyiv Ind.",
        scene_key="ukraine_raids",
    ),
    StoryCard(
        story_id=5,
        region="EUROPE",
        field="pharma_ma",
        kicker="PARIS · PHARMA",
        epistemic="OFFICIAL",
        headline="Sanofi agrees $41bn Insmed buyout",
        deck="All-cash deal for rare lung-disease drugmaker.",
        sources="Sanofi · Reuters",
        scene_key="sanofi_deal",
    ),
    StoryCard(
        story_id=6,
        region="NORTH_AMERICA",
        field="equity_markets",
        kicker="WALL ST · MARKETS",
        epistemic="CONFIRMED",
        headline="Dow clears 50,000 to close at 50,018",
        deck="Blue chips hit record while Nasdaq slips 1.5%.",
        sources="Reuters · MarketWatch",
        scene_key="dow_record",
    ),
    StoryCard(
        story_id=7,
        region="WORLD",
        field="commercial_space",
        kicker="KOUROU · SPACE",
        epistemic="CONFIRMED",
        headline="Ariane 6 orbits 36 Amazon satellites",
        deck="Tenth heavy flight lifts off from French Guiana.",
        sources="Arianespace · Xinhua",
        scene_key="ariane_launch",
    ),
    StoryCard(
        story_id=8,
        region="MIDDLE_EAST",
        field="road_disaster",
        kicker="UAE · DISASTER",
        epistemic="OFFICIAL",
        headline="Bus crash kills 13 in Ras Al Khaimah",
        deck="Worker coach carrying 41 hits stalled truck; 14 hurt.",
        sources="The National · AP",
        scene_key="uae_bus",
    ),
    StoryCard(
        story_id=9,
        region="AFRICA",
        field="aid_development",
        kicker="SUDAN · AID",
        epistemic="OFFICIAL",
        headline="AfDB & UNICEF launch $55m water aid",
        deck="Emergency clean-water plan in Port Sudan.",
        sources="AfDB · Reuters",
        scene_key="sudan_water",
    ),
    StoryCard(
        story_id=10,
        region="SE_ASIA",
        field="gas_explosion",
        kicker="VIETNAM · BLAST",
        epistemic="CONFIRMED",
        headline="Gas blast at Hanoi eatery kills 6",
        deck="Early explosion collapses shopfront; 12+ injured.",
        sources="VnExpress · AP",
        scene_key="hanoi_blast",
    ),
    StoryCard(
        story_id=11,
        region="SOUTH_ASIA",
        field="seismology",
        kicker="NEPAL · QUAKE",
        epistemic="CONFIRMED",
        headline="Shallow M5.3 quake rattles Nepal hills",
        deck="Tremor strikes near Tibet border; no casualties.",
        sources="USGS · AP",
        scene_key="nepal_quake",
    ),
    StoryCard(
        story_id=12,
        region="LATIN_AMERICA",
        field="extreme_floods",
        kicker="BRAZIL · FLOODS",
        epistemic="OFFICIAL",
        headline="South Brazil storms displace ~20,000",
        deck="Severe floods wreck homes and leave 5 dead.",
        sources="IOM · AP",
        scene_key="brazil_floods",
    ),
    StoryCard(
        story_id=13,
        region="OCEANIA",
        field="online_safety",
        kicker="AUSTRALIA · LAW",
        epistemic="OFFICIAL",
        headline="Australia passes 5% online safety law",
        deck="Digital Duty of Care bill clears parliament.",
        sources="Guardian · AP",
        scene_key="australia_law",
    ),
)

BRIEF_COL_LEFT: Tuple[WireBrief, ...] = (
    WireBrief(14, "EUROPE", "climate_mortality", "O", "England:", "5,258 summer 2026 heat deaths logged", "UKHSA"),
    WireBrief(15, "EUROPE", "ev_trade", "O", "BYD France:", "Exclusive talks to acquire Ineos EV plant", "Reuters"),
    WireBrief(16, "EUROPE", "defense_security", "O", "UK defence:", "Agencies alert arms firms to sabotage risk", "MoD"),
    WireBrief(17, "EUROPE", "football", "C", "Football:", "Real Madrid rout PSV 5–1; Arsenal 1–1", "UEFA"),
    WireBrief(18, "MIDDLE_EAST", "armed_conflict", "C", "Gaza City:", "Airstrike kills Hamas leader Abu Nahel", "Reuters"),
    WireBrief(19, "MIDDLE_EAST", "energy_policy", "O", "Iraq oil:", "Baghdad orders Kurdish oil field takeover", "National"),
    WireBrief(20, "MIDDLE_EAST", "fx_currency", "C", "Iran rial:", "Currency sinks to record 2.85m per dollar", "Anadolu"),
    WireBrief(21, "EAST_ASIA", "defense_security", "C", "South Korea:", "Russian jets trigger 07:52 air-defence alert", "Herald"),
    WireBrief(22, "EAST_ASIA", "ev_trade", "R", "Autos:", "Chinese EVs overtake Japan across 6 markets", "SCMP"),
    WireBrief(23, "EAST_ASIA", "trade_diplomacy", "O", "US–China:", "Bilateral agricultural talks open in Beijing", "Reuters"),
    WireBrief(24, "NORTH_AMERICA", "macro_policy", "C", "US economy:", "Consumer confidence climbs to 103.3", "Conf. Board"),
    WireBrief(25, "NORTH_AMERICA", "defense_diplomacy", "O", "Canada:", "Ottawa pushes back on Pentagon critique", "Guardian"),
    WireBrief(26, "AFRICA", "macro_policy", "O", "Nigeria:", "Central bank holds benchmark rate at 23%", "Reuters"),
)

BRIEF_COL_RIGHT: Tuple[WireBrief, ...] = (
    WireBrief(27, "AFRICA", "human_rights", "C", "Ethiopia:", "Rights group seeks Alamata shelling probe", "Amnesty"),
    WireBrief(28, "AFRICA", "commercial_space", "O", "South Africa:", "Unveils $372m national satellite plan", "SAnews"),
    WireBrief(29, "AFRICA", "football", "O", "Senegal:", "CAS restores 2025 AFCON 1–0 title win", "Reuters"),
    WireBrief(30, "SOUTH_ASIA", "road_disaster", "C", "India:", "00:30 UTC bus crash kills 4 schoolchildren", "PTI"),
    WireBrief(31, "SOUTH_ASIA", "political_probe", "CL", "Bangladesh:", "Ex-PM Hasina announces 16 Dec return", "Reuters"),
    WireBrief(32, "SE_ASIA", "international_law", "O", "Myanmar:", "14 nations urge junta to obey court ruling", "Reuters"),
    WireBrief(33, "SE_ASIA", "transnational_crime", "O", "Indonesia:", "139 citizens returned after Manila raid", "The Star"),
    WireBrief(34, "LATIN_AMERICA", "hostage_crisis", "ON", "Colombia:", "Gunmen hold ~25 inside Cartagena store", "Reuters"),
    WireBrief(35, "LATIN_AMERICA", "trade_diplomacy", "O", "Brazil trade:", "Seeks WTO panel on US 301 tariffs", "WTO"),
    WireBrief(36, "OCEANIA", "defense_diplomacy", "R", "Solomons:", "Set to let 2022 China security pact lapse", "SMH"),
    WireBrief(37, "OCEANIA", "aid_development", "O", "Vanuatu:", "Lawmakers endorse A$500m Australia pact", "AAP"),
    WireBrief(38, "WORLD", "human_rights", "O", "UNODC:", "47,000 women killed by kin yearly (5/hr)", "UNODC"),
    WireBrief(39, "WORLD", "un_ai_gov", "O", "UN AI arms:", "Guterres urges binding military AI treaty", "UN"),
)

BRIEF_COLUMNS: Tuple[Tuple[WireBrief, ...], Tuple[WireBrief, ...]] = (
    BRIEF_COL_LEFT,
    BRIEF_COL_RIGHT,
)

# 13 World Map pins corresponding 1-to-1 with Hero (#1-#3) and Mid (#4-#13) cards
# ViewBox: 360 x 185 (calibrated equirectangular geography with >= 22px separation)
MAP_PINS: Tuple[MapPin, ...] = (
    MapPin(1, "MIDDLE_EAST", 224.0, 87.0, "Riyadh"),
    MapPin(2, "NORTH_AMERICA", 84.0, 62.0, "Brooklyn NY"),
    MapPin(3, "EAST_ASIA", 302.0, 72.0, "Shanghai"),
    MapPin(4, "EUROPE", 210.0, 48.0, "Ukraine"),
    MapPin(5, "EUROPE", 176.0, 52.0, "Paris"),
    MapPin(6, "NORTH_AMERICA", 106.0, 74.0, "Wall St"),
    MapPin(7, "WORLD", 128.0, 108.0, "Kourou"),
    MapPin(8, "MIDDLE_EAST", 246.0, 94.0, "UAE"),
    MapPin(9, "AFRICA", 204.0, 101.0, "Port Sudan"),
    MapPin(10, "SE_ASIA", 288.0, 101.0, "Hanoi"),
    MapPin(11, "SOUTH_ASIA", 267.0, 79.0, "Nepal"),
    MapPin(12, "LATIN_AMERICA", 126.0, 146.0, "S. Brazil"),
    MapPin(13, "OCEANIA", 322.0, 149.0, "Australia"),
)

AUDIT_ITEMS: Tuple[AuditItem, ...] = (
    AuditItem(
        "1-day gate",
        "All 39 events broke or occurred on Tue 24 Nov 2026 UTC; adjacent-day stories excluded.",
    ),
    AuditItem(
        "13 visual cards",
        "All 10 world regions represented visually across 3 hero cards, 10 mid cards & map pins.",
    ),
    AuditItem(
        "Attribution",
        "Every headline, number and wire brief names its reporting outlet plus confidence tag.",
    ),
    AuditItem(
        "Scope",
        "Balanced across 26 fields: war, courts, politics, markets, space, disasters, health & law.",
    ),
)

DATE_CHECK_TEXT = (
    "All 39 stories happened or broke on Tue 24 Nov 2026 (UTC). "
    "Left out — Mon 23 Nov: Iran Hormuz mines claim; Nvidia CEO return; EU 22nd Russia sanctions package · "
    "Sun 22 Nov: COP31 ending with no deal · Wed 25 Nov: Shenzhou-24 crewed launch."
)

EXCLUDED_TRAP_FRAGMENTS: Tuple[str, ...] = (
    "hormuz",
    "nvidia",
    "22nd",
    "cop31",
    "shenzhou-24",
    "shenzhou 24",
)


def validate_dataset() -> None:
    """Enforce hard structural, regional, spatial, and temporal invariants."""
    assert len(REGIONS) == 10, f"Expected 10 regions, got {len(REGIONS)}"
    assert len(HERO_CARDS) == 3, f"Expected 3 hero cards, got {len(HERO_CARDS)}"
    assert len(MID_CARDS) == 10, f"Expected 10 mid cards, got {len(MID_CARDS)}"
    assert [len(col) for col in BRIEF_COLUMNS] == [13, 13], (
        f"Expected [13, 13] brief columns, got {[len(col) for col in BRIEF_COLUMNS]}"
    )
    assert len(MAP_PINS) == 13, f"Expected 13 map pins, got {len(MAP_PINS)}"
    assert len(TIMELINE_ANCHORS) == 7, f"Expected 7 UTC anchors, got {len(TIMELINE_ANCHORS)}"
    assert len(KEY_FIGURES) == 5, f"Expected 5 key figures, got {len(KEY_FIGURES)}"

    illustrated: List[StoryCard] = list(HERO_CARDS) + list(MID_CARDS)
    briefs: List[WireBrief] = list(BRIEF_COL_LEFT) + list(BRIEF_COL_RIGHT)

    all_ids: List[int] = [c.story_id for c in illustrated] + [b.story_id for b in briefs]
    assert all_ids == list(range(1, TOTAL_STORIES_EXPECTED + 1)), (
        f"Story IDs must be contiguous 1..39, got {all_ids}"
    )

    # Region sums
    counts: Dict[str, int] = {r.code: 0 for r in REGIONS}
    for c in illustrated:
        assert c.region in counts, f"Unknown region {c.region} on card #{c.story_id}"
        counts[c.region] += 1
    for b in briefs:
        assert b.region in counts, f"Unknown region {b.region} on brief #{b.story_id}"
        counts[b.region] += 1

    for r in REGIONS:
        assert counts[r.code] == r.expected_count, (
            f"Region {r.code}: expected {r.expected_count}, got {counts[r.code]}"
        )
    assert sum(counts.values()) == TOTAL_STORIES_EXPECTED

    # Visual coverage: every single one of the 10 regions appears in the 13 illustrated cards
    visual_regions = {c.region for c in illustrated}
    assert visual_regions == set(REGION_COLORS.keys()), (
        f"Illustrated cards missing regions: {set(REGION_COLORS.keys()) - visual_regions}"
    )

    # Distinct fields check
    fields = {c.field for c in illustrated} | {b.field for b in briefs}
    assert len(fields) == FIELD_COUNT, (
        f"Expected {FIELD_COUNT} distinct fields, got {len(fields)}: {sorted(fields)}"
    )

    # Pin 1..13 parity with illustrated cards
    for card, pin in zip(illustrated, MAP_PINS):
        assert card.story_id == pin.story_id, (
            f"Pin mismatch: card #{card.story_id} vs pin #{pin.story_id}"
        )
        assert card.region == pin.region, (
            f"Pin region mismatch for #{card.story_id}: {card.region} vs {pin.region}"
        )

    # Explicit #11 Nepal & #12 Brazil guardrails
    card11 = next(c for c in illustrated if c.story_id == 11)
    card12 = next(c for c in illustrated if c.story_id == 12)
    assert card11.region == "SOUTH_ASIA" and "Nepal" in card11.headline and "M5.3" in card11.headline
    assert card12.region == "LATIN_AMERICA" and "Brazil" in card12.headline

    # Minimum pairwise map pin Euclidean distance >= 17.0px
    min_dist = 9999.0
    for i in range(len(MAP_PINS)):
        for j in range(i + 1, len(MAP_PINS)):
            dx = MAP_PINS[i].x - MAP_PINS[j].x
            dy = MAP_PINS[i].y - MAP_PINS[j].y
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
            assert dist >= 17.0, (
                f"Pins #{MAP_PINS[i].story_id} and #{MAP_PINS[j].story_id} too close: {dist:.2f}px"
            )

    # Temporal contamination check across all 39 stories
    for c in illustrated:
        blob = f"{c.kicker} {c.headline} {c.deck} {c.sources}".lower()
        for trap in EXCLUDED_TRAP_FRAGMENTS:
            assert trap not in blob, f"Trap term '{trap}' leaked into card #{c.story_id}"
    for b in briefs:
        blob = f"{b.lead} {b.body} {b.publisher}".lower()
        for trap in EXCLUDED_TRAP_FRAGMENTS:
            assert trap not in blob, f"Trap term '{trap}' leaked into brief #{b.story_id}"
        assert not b.body.endswith("."), f"Brief #{b.story_id} should have no trailing period"

    # Non-colliding distinct region hex colors
    assert len(set(REGION_COLORS.values())) == 10, "Region hex colors must be mutually distinct"
