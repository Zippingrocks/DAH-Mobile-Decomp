#!/usr/bin/env python3
"""Render GitHub-embeddable SVG treemaps from validated progress and match reports."""
from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import math
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import source_map as sm
from tools import byte_match as bm

ROOT = Path(__file__).resolve().parents[1]
BOX = (32.0, 248.0, 1136.0, 500.0)
VIEWS = {
    "recovery": ("Source recovery", [
        ("not_started", "Not recovered", "#b83d45"),
        ("raw_output", "Raw decompiler output", "#b67b15"),
        ("repaired", "Repaired source", "#187bb2")]),
    "build": ("Source-only build", [
        ("not_tested", "Not tested", "#657587"),
        ("failed", "Build failed", "#b83d45"),
        ("passed", "Build passed", "#16866b")]),
    "behavior": ("Behavior comparison", [
        ("not_tested", "Not tested", "#657587"),
        ("differences", "Known differences", "#b83d45"),
        ("passed_scoped", "Passed within tested scope", "#16866b")]),
    "byte_match": ("Byte-match comparison", [
        ("exact_byte_match", "Exact class-file bytes", "#16866b"),
        ("normalized_match", "Normalized structure", "#187bb2"),
        ("differences", "Known structural differences", "#b83d45"),
        ("unverified", "Unverified / stale", "#657587")]),
}


def layout(rows: list[dict], box=BOX) -> list[tuple]:
    """Stable balanced binary treemap; every area represents its actual weight."""
    items = sorted(rows, key=lambda c: (-c["method_entries"], c["original"]))
    if not items:
        raise ValueError("Empty treemap")
    for item in items:
        if type(item["method_entries"]) is not int or item["method_entries"] <= 0:
            raise ValueError("Treemap weights must be positive integers")
    if not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
        raise ValueError("Invalid treemap bounds")
    def divide(items, x, y, w, h):
        if len(items) == 1:
            return [(items[0], x, y, w, h)]
        total = sum(i["method_entries"] for i in items)
        prefix, best, error = 0, 1, float("inf")
        for i, item in enumerate(items[:-1], 1):
            prefix += item["method_entries"]
            delta = abs(total/2-prefix)
            if delta < error:
                best, error = i, delta
        left, right = items[:best], items[best:]
        share = sum(i["method_entries"] for i in left)/total
        if w >= h:
            return divide(left, x, y, w*share, h) + divide(right, x+w*share, y, w*(1-share), h)
        return divide(left, x, y, w, h*share) + divide(right, x, y+h*share, w, h*(1-share))
    return divide(items, *box)


def svg(rows: list[dict], view: str, states: dict, stamp: str) -> str:
    title, legend = VIEWS[view]
    labels = {s: label for s, label, color in legend}
    colors = {s: color for s, label, color in legend}
    if set(states) != {r["original"] for r in rows} or not set(states.values()) <= set(colors):
        raise ValueError("Incomplete or unknown treemap status")
    counts = Counter(states.values())
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850" role="img" aria-labelledby="title desc">',
        f'<title id="title">DAH Mobile: {escape(title)}</title>',
        '<desc id="desc">Class-level progress treemap. Area equals original method-entry count, not coverage or accuracy. Colors reflect recorded evidence only.</desc>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif}.small{font-size:14px;fill:#526377}.label{font-size:14px;fill:white}.name{font-size:22px;font-weight:700;fill:white}</style>',
        '<rect width="1200" height="850" rx="16" fill="#f4f7fb"/>',
        '<text x="32" y="37" font-size="13" fill="#526377" letter-spacing="2">DESTROY ALL HUMANS! MOBILE / v1.2.0</text>',
        f'<text x="32" y="80" font-size="34" font-weight="700" fill="#14283f">{escape(title)}</text>',
        f'<text x="32" y="108" class="small">{len(rows)} original classes · {sum(r["method_entries"] for r in rows)} method entries · area = method count</text>',
    ]
    width = 1120/len(legend)
    for i, (state, label, color) in enumerate(legend):
        x = 32 + i*(1136/len(legend))
        parts += [f'<rect x="{x:.2f}" y="131" width="{width:.2f}" height="78" rx="8" fill="white"/>',
                  f'<rect x="{x:.2f}" y="131" width="5" height="78" rx="2" fill="{color}"/>',
                  f'<text x="{x+16:.2f}" y="158" class="small">{escape(label)}</text>',
                  f'<text x="{x+16:.2f}" y="192" font-size="28" font-weight="700" fill="#14283f">{counts[state]} / {len(rows)}</text>']
    parts.append('<text x="32" y="234" class="small">Each rectangle is one original class. Obfuscated names are retained until identified.</text>')
    for i, (row, x, y, w, h) in enumerate(layout(rows)):
        name, count = row["original"], row["method_entries"]
        state = states[name]
        parts += [f'<g data-class="{escape(name, quote=True)}" data-state="{state}">',
                  f'<title>{escape(name)}: {count} method entries; {escape(labels[state])}</title>',
                  f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{colors[state]}" stroke="#f4f7fb" stroke-width="2"/>',
                  f'<clipPath id="tile{i}"><rect x="{x+5:.3f}" y="{y+3:.3f}" width="{max(0,w-10):.3f}" height="{max(0,h-6):.3f}"/></clipPath>',
                  f'<g clip-path="url(#tile{i})">']
        if w >= 30 and h >= 30:
            size = min(22, max(11, (w-20)/(len(name)*0.65)))
            parts.append(f'<text x="{x+10:.3f}" y="{y+27:.3f}" class="name" style="font-size:{size:.2f}px">{escape(name)}</text>')
        if w >= 90 and h >= 68:
            detail = f"{count} method entries" if w >= 152 else f"{count} entries"
            parts.append(f'<text x="{x+10:.3f}" y="{y+50:.3f}" class="label">{detail}</text>')
        parts += ['</g>', '</g>']
    foot = "Exact means the entire class file. Normalized is the documented comparison policy, not a behavioral proof." if view == "byte_match" else "Recovered source, a passing build, and tested behavior are separate milestones. Green is scoped to this view."
    parts += [f'<text x="32" y="780" class="small">{escape(foot)}</text>',
              '<text x="32" y="807" class="small">Gray means untested or unverified, not failure. Class counts do not measure whole-game accuracy.</text>',
              f'<text x="32" y="832" font-size="11" fill="#526377">Metadata snapshot {escape(stamp)} · generated by tools/treemap_dashboard.py</text>', '</svg>']
    return '\n'.join(parts)+'\n'


def products(root: Path) -> dict[str, str]:
    data = sm.read_json(root / sm.MANIFEST)
    target = sm.read_json(root / "config/target.json")
    sm.validate(data, target, root, sm.tracked_files(root))
    matches, note = bm.dashboard_states(root, data, target)
    rows = data["classes"]
    states = {view: {c["original"]: c[view]["state"] for c in rows} for view in sm.STATES}
    states["byte_match"] = matches
    stamp = bm.json_digest({"classes": rows, "matches": matches, "note": note})[:16]
    result = {f"docs/{v.upper()}_TREEMAP.svg": svg(rows, v, states[v], stamp) for v in VIEWS}
    lines = ['<!-- Generated by tools/treemap_dashboard.py. -->', '# Visual progress dashboard', '',
             '[Repository home](../README.md) · [Detailed source map](SOURCE_TREE.md) · [Comparison policy](BYTE_MATCH.md)', '',
             '**Area = original method-entry count. Each box = one class. Colors = recorded status, not an accuracy score.**', '',
             '## Source recovery', '', '![Source recovery treemap](RECOVERY_TREEMAP.svg)', '',
             '## Byte-match / normalized-match', '', '![Byte-match treemap](BYTE_MATCH_TREEMAP.svg)', '',
             note, '',
             '| Match type | Classes |', '| --- | ---: |']
    count = Counter(matches.values())
    lines += [f'| {label} | {count[state]} / {len(rows)} |' for state, label, color in VIEWS['byte_match'][1]]
    lines += ['', '## Source-only build', '', '![Build treemap](BUILD_TREEMAP.svg)', '',
              '## Behavior comparison', '', '![Behavior treemap](BEHAVIOR_TREEMAP.svg)', '',
              'Behavior passes apply only to documented tests. An exact artifact match does not prove that it was rebuilt from source.', '',
              '## Refresh', '', 'These images use `config/source_map.json` and the comparison report selected in `config/byte_match.json`.',
              'The generator does not run the game or manufacture comparison results. See [maintenance](SOURCE_MAP_GUIDE.md).', '',
              '```console', 'python tools/source_map.py', 'python tools/treemap_dashboard.py',
              'python tools/treemap_dashboard.py --check', '```', '']
    result['docs/VISUAL_PROGRESS.md'] = '\n'.join(lines)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        for path, content in products(ROOT).items():
            dest = ROOT/path
            if args.check:
                if not dest.is_file() or dest.read_text(encoding='utf-8') != content:
                    raise ValueError('Stale dashboard: '+path)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding='utf-8', newline='\n')
        print('Treemaps are current.' if args.check else 'Generated GitHub treemaps. No game progress inferred.')
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('ERROR: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
