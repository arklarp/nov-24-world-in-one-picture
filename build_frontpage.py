"""Deterministic 1024x1024 RGB PNG broadsheet renderer with DOM & size auditing."""

from __future__ import annotations

import argparse
from html import escape
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
from typing import List
import zlib

from PIL import Image
from playwright.sync_api import Browser, Playwright, sync_playwright

from data import (
    AUDIT_ITEMS,
    BRIEF_COLUMNS,
    DATE_CHECK_TEXT,
    DATE_DISPLAY,
    DATE_SHORT,
    FIELD_COUNT,
    HERO_CARDS,
    KEY_FIGURES,
    MAP_PINS,
    MID_CARDS,
    REGION_COLORS,
    REGIONS,
    TIMELINE_ANCHORS,
    TOTAL_STORIES_EXPECTED,
    StoryCard,
    WireBrief,
    validate_dataset,
)
from svg_scenes import build_card_svg, build_world_map_svg

CANVAS_SIZE = 1024
MAX_PNG_BYTES = 276_480  # 270 KiB strict ceiling

EPISTEMIC_STYLES = {
    "CONFIRMED": ("#DCFCE7", "#166534", "#86EFAC"),
    "OFFICIAL": ("#DBEAFE", "#1E40AF", "#93C5FD"),
    "REPORTED": ("#FEF3C7", "#92400E", "#FCD34D"),
    "CLAIM": ("#FCE7F3", "#9D174D", "#F9A8D4"),
    "ONGOING": ("#FFEDD5", "#9A3412", "#FDBA74"),
}

CODE_TAG_STYLES = {
    "C": ("#DCFCE7", "#166534", "#86EFAC"),
    "O": ("#DBEAFE", "#1E40AF", "#93C5FD"),
    "R": ("#FEF3C7", "#92400E", "#FCD34D"),
    "CL": ("#FCE7F3", "#9D174D", "#F9A8D4"),
    "ON": ("#FFEDD5", "#9A3412", "#FDBA74"),
}

NUM_TOKEN_RE = re.compile(r"(\$?\d[\d,\.]*(?:bn|m|k|%)?)", re.IGNORECASE)


def _highlight_numbers(text: str) -> str:
    """Wrap numeric tokens in tabular-nums spans for crisp visual legibility."""
    escaped = escape(text)
    return NUM_TOKEN_RE.sub(r'<span class="hl-num">\1</span>', escaped)


def _render_epistemic_pill(label: str) -> str:
    bg, fg, border = EPISTEMIC_STYLES[label]
    return (
        f'<span class="epi-pill" style="background:{bg};color:{fg};'
        f'border:1px solid {border};">{escape(label)}</span>'
    )


def _render_hero_card(card: StoryCard) -> str:
    reg_color = REGION_COLORS[card.region]
    svg = build_card_svg(card.scene_key, card.story_id, card.region)
    return (
        f'<article class="hero-card" data-story-id="{card.story_id}" '
        f'data-region-color="{reg_color}" style="--reg:{reg_color};">'
        f'<div class="card-meta">'
        f'<span class="card-kicker" style="color:{reg_color};">{escape(card.kicker)}</span>'
        f'{_render_epistemic_pill(card.epistemic)}'
        f'</div>'
        f'<div class="hero-art">{svg}</div>'
        f'<h2 class="hero-hl">{_highlight_numbers(card.headline)}</h2>'
        f'<p class="hero-deck">{escape(card.deck)}</p>'
        f'<div class="hero-src">Source: <b>{escape(card.sources)}</b></div>'
        f'</article>'
    )


def _render_mid_card(card: StoryCard) -> str:
    reg_color = REGION_COLORS[card.region]
    svg = build_card_svg(card.scene_key, card.story_id, card.region)
    return (
        f'<article class="mid-card" data-story-id="{card.story_id}" '
        f'data-region-color="{reg_color}" style="--reg:{reg_color};">'
        f'<div class="card-meta">'
        f'<span class="mid-kicker" style="color:{reg_color};">{escape(card.kicker)}</span>'
        f'{_render_epistemic_pill(card.epistemic)}'
        f'</div>'
        f'<div class="mid-art">{svg}</div>'
        f'<h3 class="mid-hl">{_highlight_numbers(card.headline)}</h3>'
        f'<p class="mid-deck">{escape(card.deck)}</p>'
        f'<div class="mid-src">{escape(card.sources)}</div>'
        f'</article>'
    )


def _render_brief_row(brief: WireBrief) -> str:
    reg_color = REGION_COLORS[brief.region]
    bg, fg, border = CODE_TAG_STYLES[brief.epistemic_code]
    return (
        f'<div class="b-row" data-story-id="{brief.story_id}">'
        f'<span class="b-id" style="background:{reg_color};">{brief.story_id}</span>'
        f'<span class="b-text">'
        f'<b class="b-lead">{escape(brief.lead)}</b> '
        f'{escape(brief.body)} '
        f'<b class="b-dot">&middot;</b> '
        f'<b class="b-pub">{escape(brief.publisher)}</b>'
        f'</span>'
        f'<span class="b-tag" style="background:{bg};color:{fg};border:1px solid {border};">'
        f'{escape(brief.epistemic_code)}</span>'
        f'</div>'
    )


def build_html() -> str:
    """Assemble deterministic self-contained HTML + CSS for the 1024x1024 canvas."""
    region_chips = "".join(
        f'<div class="reg-chip" style="background:{r.color};">'
        f'<span class="chip-lbl">{escape(r.label)}</span>'
        f'<span class="chip-cnt">{r.expected_count}</span>'
        f'</div>'
        for r in REGIONS
    )

    timeline_items = '<span class="utc-sep">&bull;</span>'.join(
        f'<span class="utc-item"><b>{escape(a.utc)}</b> {escape(a.label)}</span>'
        for a in TIMELINE_ANCHORS
    )

    number_cells = "".join(
        f'<div class="num-cell">'
        f'<div class="num-val" style="color:{n.accent};">{escape(n.value)}</div>'
        f'<div class="num-cap">{escape(n.caption)}</div>'
        f'</div>'
        for n in KEY_FIGURES
    )

    heroes_html = "".join(_render_hero_card(c) for c in HERO_CARDS)
    mids_html = "".join(_render_mid_card(c) for c in MID_CARDS)
    left_briefs = "".join(_render_brief_row(b) for b in BRIEF_COLUMNS[0])
    right_briefs = "".join(_render_brief_row(b) for b in BRIEF_COLUMNS[1])
    map_svg = build_world_map_svg(MAP_PINS)

    audit_html = "".join(
        f'<div class="chk-item"><b>{escape(item.label)}:</b> {escape(item.detail)}</div>'
        for item in AUDIT_ITEMS
    )

    css = """
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
html, body {
  width: 1024px;
  height: 1024px;
  overflow: hidden;
  background: #FAF8F3;
  color: #0F172A;
  font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page {
  width: 1024px;
  height: 1024px;
  overflow: hidden;
  padding: 5px 11px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  background: #FAF8F3;
}
/* 1. Top Meta Bar (17px) */
.top-meta {
  height: 17px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1.5px solid #0F172A;
  padding-bottom: 1px;
}
.meta-kicker {
  font-size: 10.6px;
  font-weight: 900;
  letter-spacing: 0.55px;
  color: #991B1B;
  text-transform: uppercase;
}
.meta-counts {
  font-size: 10.2px;
  font-weight: 800;
  letter-spacing: 0.25px;
  color: #0F172A;
  font-variant-numeric: tabular-nums;
}
/* 2. Masthead & Subhead (52px) */
.masthead-wrap {
  height: 52px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-bottom: 1px solid #D6CFC1;
  padding-bottom: 2px;
}
.masthead-row {
  height: 36px;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
h1.masthead {
  font-family: Georgia, serif;
  font-size: 36px;
  line-height: 0.96;
  font-weight: 900;
  color: #020617;
  letter-spacing: -0.35px;
}
.edition-stamp {
  font-size: 9.6px;
  font-weight: 800;
  color: #475569;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  border: 1px solid #CBD5E1;
  background: #FFFFFF;
  padding: 2px 6px;
  border-radius: 2px;
}
p.subhead {
  height: 14px;
  font-size: 11.4px;
  line-height: 14px;
  font-weight: 700;
  color: #991B1B;
  white-space: nowrap;
  overflow: hidden;
}
/* 3. Region Chips 5x2 (34px) */
.region-grid {
  height: 34px;
  flex-shrink: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(2, 15.5px);
  gap: 3px 5px;
}
.reg-chip {
  height: 15.5px;
  border-radius: 2.5px;
  padding: 0 3px 0 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
}
.chip-lbl {
  font-size: 10.1px;
  font-weight: 800;
  letter-spacing: 0.3px;
}
.chip-cnt {
  background: rgba(0, 0, 0, 0.34);
  color: #FFFFFF;
  font-size: 10.1px;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  line-height: 12.5px;
  padding: 0 5px;
  border-radius: 2px;
  min-width: 17px;
  text-align: center;
}
/* 4. UTC Chronology Strip (18px) */
.utc-strip {
  height: 18px;
  flex-shrink: 0;
  background: #F3EFE6;
  border: 1px solid #D6CFC1;
  border-radius: 2.5px;
  display: flex;
  align-items: center;
  overflow: hidden;
}
.utc-badge {
  height: 100%;
  background: #991B1B;
  color: #FFFFFF;
  font-size: 9.4px;
  font-weight: 900;
  letter-spacing: 0.5px;
  padding: 0 7px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.utc-track {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  padding: 0 4px;
  white-space: nowrap;
}
.utc-item {
  font-size: 10.1px;
  color: #1E293B;
  font-variant-numeric: tabular-nums;
}
.utc-item b {
  color: #020617;
  font-weight: 900;
}
.utc-sep {
  color: #94A3B8;
  font-size: 8px;
}
/* 5. IN NUMBERS Bar (32px) */
.numbers-bar {
  height: 32px;
  flex-shrink: 0;
  display: flex;
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  border-radius: 2.5px;
  overflow: hidden;
}
.num-badge {
  background: #0F172A;
  color: #FACC15;
  font-size: 8.8px;
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: 0.5px;
  padding: 0 9px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  flex-shrink: 0;
}
.num-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}
.num-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-left: 1px solid #E2E8F0;
  padding: 1px 4px;
  overflow: hidden;
}
.num-val {
  font-size: 14.8px;
  line-height: 1.05;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.1px;
}
.num-cap {
  font-size: 8.4px;
  line-height: 1.1;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
}
/* 6. Top 3 Hero Cards (202px) */
.hero-grid {
  height: 202px;
  flex-shrink: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 7px;
}
.hero-card {
  background: #FFFBF2;
  border: 1px solid #DDD4C3;
  border-top: 4px solid var(--reg);
  border-radius: 3px;
  padding: 4px 6px 3.5px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}
.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  flex-shrink: 0;
}
.card-kicker {
  font-size: 9.2px;
  font-weight: 900;
  letter-spacing: 0.35px;
  white-space: nowrap;
}
.epi-pill {
  font-size: 7.4px;
  font-weight: 900;
  letter-spacing: 0.25px;
  padding: 0.5px 4px;
  border-radius: 2px;
  line-height: 1.15;
  flex-shrink: 0;
}
.hero-art {
  width: 100%;
  height: 82px;
  border: 1px solid #E5DDD0;
  border-radius: 2px;
  overflow: hidden;
  flex-shrink: 0;
}
.hero-art svg, .mid-art svg {
  width: 100%;
  height: 100%;
  display: block;
}
.hero-hl {
  font-size: 17.5px;
  line-height: 1.05;
  font-weight: 900;
  color: #020617;
  letter-spacing: 0.06px;
}
.hl-num {
  font-variant-numeric: tabular-nums;
  font-weight: 900;
}
.hero-deck {
  font-size: 10.2px;
  line-height: 1.15;
  color: #1E293B;
}
.hero-src {
  font-size: 8.7px;
  line-height: 1.1;
  color: #475569;
  border-top: 1px solid #E5DDD0;
  padding-top: 2px;
  white-space: nowrap;
}
.hero-src b {
  color: #0F172A;
}
/* 7. Mid 5x2 Cards (284px) */
.mid-grid {
  height: 284px;
  flex-shrink: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 4.5px 5.5px;
}
.mid-card {
  background: #FFFFFF;
  border: 1px solid #D8D2C6;
  border-top: 3.5px solid var(--reg);
  border-radius: 3px;
  padding: 3px 5px 2.5px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}
.mid-kicker {
  font-size: 7.9px;
  font-weight: 900;
  letter-spacing: 0.25px;
  white-space: nowrap;
}
.mid-card .epi-pill {
  font-size: 6.8px;
  padding: 0.5px 3px;
}
.mid-art {
  width: 100%;
  height: 47px;
  border: 1px solid #E5E0D6;
  border-radius: 2px;
  overflow: hidden;
  flex-shrink: 0;
}
.mid-hl {
  font-size: 11.7px;
  line-height: 1.05;
  font-weight: 900;
  color: #020617;
  letter-spacing: 0.05px;
}
.mid-deck {
  font-size: 8.9px;
  line-height: 1.10;
  color: #334155;
}
.mid-src {
  font-size: 8.1px;
  line-height: 1.08;
  font-weight: 800;
  color: #1E293B;
  border-top: 1px solid #ECE7DF;
  padding-top: 1.5px;
  white-space: nowrap;
}
/* 8. Lower Split Tier (flex: 1, ~309px) */
.lower-tier {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr 246px;
  gap: 6px;
}
.panel-box {
  background: #FFFFFF;
  border: 1px solid #D8D2C6;
  border-top: 2.5px solid #0F172A;
  border-radius: 3px;
  padding: 4px 7px 3px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.panel-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1.2px solid #0F172A;
  padding-bottom: 2px;
  margin-bottom: 3px;
  flex-shrink: 0;
}
.panel-title {
  font-size: 9.8px;
  font-weight: 900;
  letter-spacing: 0.35px;
  color: #020617;
  text-transform: uppercase;
}
.panel-key {
  font-size: 8.3px;
  font-weight: 700;
  color: #475569;
  white-space: nowrap;
}
.brief-cols {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.brief-col {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.b-row {
  height: 19px;
  display: flex;
  align-items: center;
  gap: 4px;
  border-bottom: 1px solid #ECE7DF;
  font-size: 10.5px;
  line-height: 1.1;
  min-width: 0;
}
.b-row:last-child {
  border-bottom: none;
}
.b-id {
  width: 18.5px;
  height: 14px;
  border-radius: 2px;
  color: #FFFFFF;
  font-size: 8.7px;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.b-text {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  color: #0F172A;
  font-size: 10.5px;
}
.b-lead {
  font-weight: 800;
  color: #020617;
}
.b-dot {
  font-weight: 900;
  color: #64748B;
}
.b-pub {
  font-weight: 800;
  color: #1E293B;
}
.b-tag {
  width: 16px;
  height: 13.5px;
  border-radius: 2px;
  font-size: 7.3px;
  font-weight: 900;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
/* Right Sidebar (246px) */
.sidebar {
  width: 246px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.map-panel {
  background: #FFFFFF;
  border: 1px solid #D8D2C6;
  border-top: 2.5px solid #0F172A;
  border-radius: 3px;
  padding: 4px 5px 3px;
  display: flex;
  flex-direction: column;
  gap: 2.5px;
  flex-shrink: 0;
  overflow: hidden;
}
.side-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #CBD5E1;
  padding-bottom: 1.5px;
}
.side-title {
  font-size: 8.9px;
  font-weight: 900;
  letter-spacing: 0.3px;
  color: #020617;
}
.side-meta {
  font-size: 8.2px;
  font-weight: 800;
  color: #991B1B;
}
.map-frame {
  width: 100%;
  border: 1px solid #CBD5E1;
  border-radius: 2px;
  overflow: hidden;
  line-height: 0;
}
.map-frame svg {
  width: 100%;
  height: auto;
  display: block;
}
.map-cap {
  font-size: 8.0px;
  line-height: 1.15;
  font-weight: 700;
  color: #334155;
  text-align: center;
  white-space: nowrap;
}
.how-panel {
  flex: 1;
  min-height: 0;
  background: #FFFDF8;
  border: 1px solid #D8D2C6;
  border-top: 2.5px solid #991B1B;
  border-radius: 3px;
  padding: 4px 5px 4px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow: hidden;
}
.chk-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 3px;
}
.chk-item {
  background: #F8F3E8;
  border-left: 2.5px solid #991B1B;
  padding: 2.5px 5px;
  font-size: 8.25px;
  line-height: 1.16;
  color: #1E293B;
  border-radius: 0 2px 2px 0;
  overflow: hidden;
}
.chk-item b {
  color: #020617;
  font-weight: 900;
}
/* 9. Date-Check & Footer (~39px) */
.bottom-band {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 2.5px;
}
.date-check {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-left: 3px solid #991B1B;
  border-radius: 2.5px;
  padding: 2.5px 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}
.dc-badge {
  background: #991B1B;
  color: #FFFFFF;
  font-size: 8.4px;
  font-weight: 900;
  letter-spacing: 0.35px;
  padding: 1.5px 5px;
  border-radius: 2px;
  flex-shrink: 0;
}
.dc-body {
  font-size: 9.9px;
  line-height: 1.15;
  color: #450A0A;
  font-weight: 600;
}
.footer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 8.4px;
  line-height: 1.1;
  color: #334155;
  padding: 0 1px;
}
.footer-legend b {
  color: #020617;
}
.footer-note {
  font-weight: 700;
  color: #475569;
}
"""

    subhead = (
        "Riyadh tower hit & Saudi retaliation · Brooklyn jury convicts Huawei on 10 of 12 counts · "
        "Shanghai party chief probed · Ukraine dawn raids · Sanofi $41bn buyout · Dow 50,018"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{escape(DATE_DISPLAY)} — World News in One Picture</title>
<style>{css}</style>
</head>
<body>
<main class="page">
  <header class="top-meta">
    <span class="meta-kicker">GLOBAL DAILY DISPATCH &middot; WORLD IN ONE PICTURE</span>
    <span class="meta-counts">{TOTAL_STORIES_EXPECTED} DATED STORIES &middot; {len(REGIONS)} REGIONS &middot; {FIELD_COUNT} FIELDS &middot; ALL {escape(DATE_SHORT)}</span>
  </header>

  <section class="masthead-wrap">
    <div class="masthead-row">
      <h1 class="masthead">{escape(DATE_DISPLAY)}</h1>
      <span class="edition-stamp">SINGLE-DAY EDITION &middot; UTC</span>
    </div>
    <p class="subhead">{escape(subhead)}</p>
  </section>

  <section class="region-grid" aria-label="Stories by world region">
    {region_chips}
  </section>

  <section class="utc-strip" aria-label="24-hour UTC chronology">
    <span class="utc-badge">UTC</span>
    <div class="utc-track">{timeline_items}</div>
  </section>

  <section class="numbers-bar" aria-label="Key figures">
    <div class="num-badge"><span>IN</span><span>NUMBERS</span></div>
    <div class="num-grid">{number_cells}</div>
  </section>

  <section class="hero-grid" aria-label="Top three stories">
    {heroes_html}
  </section>

  <section class="mid-grid" aria-label="Ten regional illustrated stories">
    {mids_html}
  </section>

  <section class="lower-tier">
    <div class="panel-box">
      <div class="panel-hdr">
        <span class="panel-title">ALSO ON TUESDAY 24 NOVEMBER &middot; 26 MORE STORIES</span>
        <span class="panel-key"><b>C</b> Confirmed &middot; <b>O</b> Official &middot; <b>R</b> Reported &middot; <b>CL</b> Claim &middot; <b>ON</b> Ongoing</span>
      </div>
      <div class="brief-cols">
        <div class="brief-col">{left_briefs}</div>
        <div class="brief-col">{right_briefs}</div>
      </div>
    </div>

    <aside class="sidebar">
      <div class="map-panel">
        <div class="side-hdr">
          <span class="side-title">WHERE IT HAPPENED</span>
          <span class="side-meta">Pins 1&ndash;13</span>
        </div>
        <div class="map-frame">{map_svg}</div>
        <div class="map-cap">All 13 visual cards plotted &middot; hues match region chips</div>
      </div>

      <div class="how-panel">
        <div class="side-hdr">
          <span class="side-title">HOW THIS PAGE WAS CHECKED</span>
          <span class="side-meta">39 / 39 UTC</span>
        </div>
        <div class="chk-list">{audit_html}</div>
      </div>
    </aside>
  </section>

  <footer class="bottom-band">
    <div class="date-check">
      <span class="dc-badge">DATE CHECK</span>
      <span class="dc-body">{escape(DATE_CHECK_TEXT)}</span>
    </div>
    <div class="footer-bar">
      <span class="footer-legend"><b>Tags:</b> C Confirmed &middot; O Official &middot; R Reported &middot; CL Claim &middot; ON Ongoing</span>
      <span class="footer-note">Original vector illustrations &middot; every story names its sources</span>
    </div>
  </footer>
</main>
</body>
</html>
"""


DOM_AUDIT_JS = r"""() => {
  const errs = [];
  const docEl = document.documentElement;
  if (docEl.scrollWidth > 1024 || docEl.scrollHeight > 1024) {
    errs.push(`Canvas overflow: ${docEl.scrollWidth}x${docEl.scrollHeight}`);
  }
  const page = document.querySelector('.page');
  if (page && (page.scrollWidth > 1024 || page.scrollHeight > 1024)) {
    errs.push(`.page overflow: ${page.scrollWidth}x${page.scrollHeight}`);
  }

  // Unique masthead heading check
  const h1s = document.querySelectorAll('h1');
  if (h1s.length !== 1) {
    errs.push(`Expected 1 h1 masthead, found ${h1s.length}`);
  }

  // Container overflow check
  const boxSelectors = [
    '.hero-card', '.mid-card', '.panel-box', '.numbers-bar', '.utc-strip',
    '.date-check', '.map-panel', '.how-panel', '.chk-item', '.map-cap'
  ];
  for (const sel of boxSelectors) {
    document.querySelectorAll(sel).forEach((el, idx) => {
      if (el.scrollHeight > el.clientHeight + 1.0) {
        errs.push(`Vertical overflow on ${sel}[${idx}]: scrollH=${el.scrollHeight} > clientH=${el.clientHeight}`);
      }
      if (el.scrollWidth > el.clientWidth + 1.0) {
        errs.push(`Horizontal overflow on ${sel}[${idx}]: scrollW=${el.scrollWidth} > clientW=${el.clientWidth}`);
      }
    });
  }

  // Single-line text clipping checks
  const singleLineSelectors = ['.subhead', '.reg-chip', '.b-row .b-text'];
  for (const sel of singleLineSelectors) {
    document.querySelectorAll(sel).forEach((el, idx) => {
      if (el.scrollWidth > el.clientWidth + 0.5) {
        errs.push(`Text clip on ${sel}[${idx}] ("${el.textContent.slice(0, 42)}"): scrollW=${el.scrollWidth} > clientW=${el.clientWidth}`);
      }
    });
  }

  // Brief row wrapping check
  document.querySelectorAll('.b-row').forEach((row) => {
    const id = row.getAttribute('data-story-id');
    const cs = getComputedStyle(row);
    const lh = parseFloat(cs.lineHeight) || 12;
    if (row.clientHeight > 26 || (row.clientHeight / lh) > 2.1) {
      errs.push(`Brief row #${id} unexpectedly tall: clientHeight=${row.clientHeight}, lineHeight=${lh}`);
    }
  });

  // Per-SVG geometry, pill margin, and pin collision checks
  document.querySelectorAll('svg').forEach((svg, idx) => {
    const vb = (svg.getAttribute('viewBox') || '').split(/\s+/).map(Number);
    if (vb.length !== 4) return;
    const [vx, vy, vw, vh] = vb;

    svg.querySelectorAll('text').forEach((t) => {
      const bb = t.getBBox();
      if (bb.x < vx - 0.5 || bb.y < vy - 0.5 || bb.x + bb.width > vx + vw + 0.5 || bb.y + bb.height > vy + vh + 0.5) {
        errs.push(`SVG[${idx}] text "${t.textContent}" outside viewBox`);
      }
    });

    svg.querySelectorAll('text[data-pill-for]').forEach((t) => {
      const rectId = t.getAttribute('data-pill-for');
      const rect = svg.getElementById(rectId);
      if (!rect) {
        errs.push(`SVG[${idx}] missing pill rect #${rectId}`);
        return;
      }
      const tb = t.getBBox();
      const rb = rect.getBBox();
      const padL = tb.x - rb.x;
      const padR = (rb.x + rb.width) - (tb.x + tb.width);
      const padT = tb.y - rb.y;
      const padB = (rb.y + rb.height) - (tb.y + tb.height);
      if (padL < 0.8 || padR < 0.8 || padT < 0.8 || padB < 0.8) {
        errs.push(`SVG[${idx}] pill #${rectId} ("${t.textContent}") tight margin: L=${padL.toFixed(1)} R=${padR.toFixed(1)} T=${padT.toFixed(1)} B=${padB.toFixed(1)}`);
      }
    });

    const pin = svg.querySelector('.card-pin');
    if (pin) {
      const pb = pin.getBBox();
      svg.querySelectorAll('.callout-pill').forEach((pill) => {
        const cb = pill.getBBox();
        const overlapX = pb.x < cb.x + cb.width + 1 && pb.x + pb.width + 1 > cb.x;
        const overlapY = pb.y < cb.y + cb.height + 1 && pb.y + pb.height + 1 > cb.y;
        if (overlapX && overlapY) {
          errs.push(`SVG[${idx}] callout pill overlaps .card-pin`);
        }
      });
    }
  });

  // Card-to-pin parity (num + color)
  document.querySelectorAll('article[data-story-id]').forEach((card) => {
    const id = card.getAttribute('data-story-id');
    const col = card.getAttribute('data-region-color');
    const pin = card.querySelector('.card-pin');
    if (!pin) {
      errs.push(`Card #${id} missing .card-pin`);
      return;
    }
    if (pin.getAttribute('data-pin-num') !== id || pin.getAttribute('data-pin-color') !== col) {
      errs.push(`Card #${id} pin parity mismatch`);
    }
  });

  return errs;
}"""


def _launch_browser(pw: Playwright) -> Browser:
    """Launch headless Chromium with clean cross-platform fallbacks."""
    launch_args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-lcd-text"]
    attempts = [
        {"args": launch_args},
        {"channel": "chrome", "args": launch_args},
        {"channel": "msedge", "args": launch_args},
    ]
    candidate_paths: List[str] = [
        "/home/ubuntu/.local/bin/chromium",
        "/home/ubuntu/.local/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            attempts.append({"executable_path": path, "args": launch_args})

    last_err: Exception | None = None
    for kwargs in attempts:
        try:
            return pw.chromium.launch(**kwargs)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"Failed to launch Chromium browser: {last_err}")


def _encode_rgb_png_filter0(rgb: Image.Image) -> bytes:
    """Deterministically encode a lossless 8-bit 3-channel RGB PNG using Filter 0."""
    width, height = rgb.size
    raw = rgb.tobytes()
    stride = width * 3
    scanlines = b"".join(b"\x00" + raw[y * stride : (y + 1) * stride] for y in range(height))

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15, memLevel=9)
    idat = compressor.compress(scanlines) + compressor.flush()
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def _write_compact_rgb_png(rgb: Image.Image, output_path: Path) -> None:
    """Write the smallest deterministic 3-channel RGB PNG under MAX_PNG_BYTES."""
    # First write via Pillow optimize=True, compress_level=9
    rgb.save(output_path, format="PNG", optimize=True, compress_level=9)
    pil_size = output_path.stat().st_size

    # Compare against lossless Filter-0 3-channel RGB PNG (ideal for flat editorial vectors)
    f0_bytes = _encode_rgb_png_filter0(rgb)
    if len(f0_bytes) < pil_size:
        output_path.write_bytes(f0_bytes)

    # If still marginally above ceiling, gently snap near-identical antialiased RGB levels (step=2)
    if output_path.stat().st_size > MAX_PNG_BYTES:
        snapped = rgb.point(lambda v: (v & 0xFE))
        f0_snapped = _encode_rgb_png_filter0(snapped)
        if len(f0_snapped) <= MAX_PNG_BYTES:
            output_path.write_bytes(f0_snapped)


def render_entry(output_path: Path) -> int:
    """Validate dataset, render HTML via Playwright, audit DOM, save RGB PNG."""
    validate_dataset()
    html = build_html()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        raw_png = Path(tmp.name)

    try:
        with sync_playwright() as pw:
            browser = _launch_browser(pw)
            try:
                page = browser.new_page(
                    viewport={"width": CANVAS_SIZE, "height": CANVAS_SIZE},
                    device_scale_factor=1,
                )
                page.set_content(html, wait_until="load")
                page.evaluate("() => document.fonts.ready")
                audit_errors = page.evaluate(DOM_AUDIT_JS)
                if audit_errors:
                    joined = "\n  - ".join(audit_errors)
                    raise RuntimeError(f"DOM audit failed with {len(audit_errors)} issue(s):\n  - {joined}")
                page.screenshot(path=str(raw_png), full_page=False)
            finally:
                browser.close()

        with Image.open(raw_png) as img:
            rgb = img.convert("RGB")
            if rgb.size != (CANVAS_SIZE, CANVAS_SIZE):
                raise RuntimeError(f"Unexpected dimensions {rgb.size}, expected {CANVAS_SIZE}x{CANVAS_SIZE}")
            _write_compact_rgb_png(rgb, output_path)
    finally:
        if raw_png.exists():
            raw_png.unlink()

    # Final binary & pillow verification
    byte_size = output_path.stat().st_size
    with Image.open(output_path) as check:
        if check.size != (CANVAS_SIZE, CANVAS_SIZE) or check.mode != "RGB":
            raise RuntimeError(f"Output verification failed: size={check.size}, mode={check.mode}")
    if byte_size > MAX_PNG_BYTES:
        raise RuntimeError(
            f"PNG size {byte_size} bytes exceeds {MAX_PNG_BYTES} byte (270 KiB) ceiling"
        )
    return byte_size


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic 1024x1024 Tue 24 Nov 2026 infographic.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "entry.png",
        help="Destination path for the rendered RGB PNG.",
    )
    args = parser.parse_args(argv)
    size = render_entry(args.output)
    print(f"OK: wrote {args.output} ({size:,} bytes, {size / 1024:.1f} KiB, 1024x1024 RGB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
