#!/usr/bin/env python3
"""Verify a general-purpose Skill bundle and domain-neutral smoke tests.

The checks validate package structure and sample math/contract structure,
NOT the quality of any particular lesson or user-facing visualization.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REQUIRED=[
    "SKILL.md","README.md","CHANGELOG.md",
    "references/angle-evidence.md",
    "references/camera-controls.md",
    "references/continuity-protocol.md",
    "references/domain-recipes.md",
    "references/geometry-math.md",
    "references/quality-checks.md",
    "references/teaching-sequence.md",
    "references/transition-patterns.md",
    "references/verification-workflow.md",
    "assets/interactive-starter.html",
    "assets/continuous-vector-starter.html",
    "assets/example-vector-storyboard.json",
    "assets/example-visual-contract.json",
    "scripts/validate_continuity.py",
    "scripts/validate_visual_contract.py",
    "scripts/test_visual_contract_failures.py",
    "scripts/check_vector_math.py",
    "scripts/check_offline_html.py",
    "scripts/capture_lesson_frames.py",
]
COMMANDS=[
    ["scripts/validate_continuity.py","assets/example-vector-storyboard.json"],
    ["scripts/validate_visual_contract.py","assets/example-visual-contract.json"],
    ["scripts/test_visual_contract_failures.py"],
    ["scripts/check_vector_math.py"],
    ["scripts/check_offline_html.py","assets/interactive-starter.html"],
    ["scripts/check_offline_html.py","assets/continuous-vector-starter.html"],
]


def main():
    missing=[rel for rel in REQUIRED if not (ROOT/rel).is_file()]
    if missing:
        for rel in missing:print("FAIL missing:",rel)
        return 1
    txt=(ROOT/"SKILL.md").read_text(encoding="utf-8")
    if not txt.startswith("---\n") or "name: spatial-geometry-explainer" not in txt[:350]:
        print("FAIL: invalid Skill frontmatter/name")
        return 1
    print(f"PASS: {len(REQUIRED)} mandatory general-purpose files and Skill entrypoint")
    for cmd in COMMANDS:
        result=subprocess.run([sys.executable,*cmd],
                cwd=ROOT,capture_output=True,text=True)
        print(f"\n$ python {' '.join(cmd)}")
        print(result.stdout.strip())
        if result.returncode:
            if result.stderr:print(result.stderr[-1500:],file=sys.stderr)
            print("FAIL command returncode:",result.returncode)
            return 1
    print("\nPASS: generic package structure, provenance contracts, visual contract structure, vector math")
    print("NOT RUN: application-specific mathematical modeling, browser readability or actual human learning review")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
