#!/usr/bin/env python3
"""Check the explicit provenance/handoff structure of an interactive lesson plan.

This is a *structural* check. It cannot replace vector-math checks, browser
screenshots, human reading, or an animation continuity test.
Usage: python scripts/validate_continuity.py assets/example-vector-storyboard.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED = {
    "define", "measure-angle", "project", "subtract", "add", "transform-frame",
    "translate-copy", "rotate-object", "cross", "scale", "compare",
}
OPERATIONS_WITH_SOURCE = ALLOWED - {"define"}
ANIMATED_REQUIRED = {"translate-copy", "rotate-object", "transform-frame"}


def validate(data):
    errors = []
    quantities = data.get("quantities", [])
    stages = data.get("stages", [])
    if not isinstance(quantities, list) or not isinstance(stages, list):
        return ["quantities and stages must be arrays"]
    q = {}
    for item in quantities:
        if not isinstance(item, dict) or not item.get("id"):
            errors.append("A quantity lacks id")
            continue
        key = item["id"]
        if key in q:
            errors.append(f"Duplicate quantity id: {key}")
        q[key] = item
        if not item.get("kind") or not item.get("frame"):
            errors.append(f"{key}: expected kind and frame")
        if item.get("kind") in ("vector", "scalar") and not item.get("unit"):
            errors.append(f"{key}: missing unit")
    visible = set()
    created = set()
    for i, stage in enumerate(stages):
        if not isinstance(stage, dict):
            errors.append(f"stage {i+1}: not an object")
            continue
        name = stage.get("title", f"stage {i+1}")
        if not stage.get("question") or not stage.get("evidence"):
            errors.append(f"{name}: missing question or on-screen evidence")
        incoming = stage.get("retains", [])
        new_ids = stage.get("introduces", [])
        actions = stage.get("actions", [])
        if not isinstance(incoming, list) or not isinstance(new_ids, list) or not isinstance(actions, list):
            errors.append(f"{name}: retains/introduces/actions must be arrays")
            continue
        if i and not (set(incoming) & visible):
            errors.append(f"{name}: no visual handoff from previous stage")
        for src in incoming:
            if src not in created:
                errors.append(f"{name}: retained quantity {src} was not introduced earlier")
        local = set(created)
        introduced_by_action = set()
        for action in actions:
            op = action.get("type")
            res = action.get("result")
            src = action.get("source")
            if op not in ALLOWED:
                errors.append(f"{name}: unsupported operation {op!r}")
            if not res or res not in q:
                errors.append(f"{name}: missing or unknown result {res!r}")
                continue
            if op in OPERATIONS_WITH_SOURCE:
                if not src or src not in local:
                    errors.append(f"{name}: {res} has no earlier source {src!r}")
                elif src not in incoming and src not in introduced_by_action:
                    errors.append(f"{name}: source {src} not visibly retained during operation")
            if op in {"add", "subtract", "cross"}:
                inputs = action.get("inputs")
                if not isinstance(inputs, list) or len(inputs) < 2:
                    errors.append(f"{name}: {res} needs at least two explicit math inputs")
                else:
                    for dep in inputs:
                        if dep not in local:
                            errors.append(f"{name}: {res} has unavailable math input {dep}")
                        elif dep not in incoming and dep not in introduced_by_action:
                            errors.append(f"{name}: math input {dep} not visibly retained")
                    if src and src not in inputs:
                        errors.append(f"{name}: source {src} missing from explicit math inputs")
            if op in {"measure-angle", "project", "transform-frame"}:
                basis = action.get("basis")
                if not basis or basis not in local:
                    errors.append(f"{name}: {op} {res} lacks available reference basis")
            if op in ANIMATED_REQUIRED:
                if action.get("animated") is not True:
                    errors.append(f"{name}: {op} {res} must be visibly animated")
                if op == "translate-copy" and action.get("keep_source_visible") is not True:
                    errors.append(f"{name}: {res} copy must keep a visible source/ghost")
            if res in introduced_by_action or res in created:
                errors.append(f"{name}: repeated creation of {res}")
            introduced_by_action.add(res)
            local.add(res)
        for result in new_ids:
            if result not in q:
                errors.append(f"{name}: undeclared quantity {result}")
            if result in created:
                errors.append(f"{name}: quantity {result} introduced twice")
            if result not in introduced_by_action:
                errors.append(f"{name}: quantity {result} appears without an operation")
        missing = introduced_by_action - set(new_ids)
        for result in sorted(missing):
            errors.append(f"{name}: operation result {result} not listed under introduces")
        visible = set(incoming) | set(new_ids)
        created.update(new_ids)
    for key in q:
        if key not in created:
            errors.append(f"Declared but never introduced quantity: {key}")
    if not stages:
        errors.append("No stages")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    ns = parser.parse_args()
    try:
        data = json.loads(ns.storyboard.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: could not read storyboard: {exc}")
        return 2
    problems = validate(data)
    for problem in problems:
        print("FAIL:", problem)
    if problems:
        print(f"FAIL: {len(problems)} continuity issue(s)")
        return 1
    print(f"PASS: {len(data['stages'])} stages and {len(data['quantities'])} quantity IDs have traceable structural handoffs")
    print("REMINDER: still inspect math, rendered geometry, animation frames, and mobile layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
