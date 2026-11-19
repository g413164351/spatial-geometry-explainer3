#!/usr/bin/env python3
"""Validate a visual angle/handoff *specification*, not rendered pixels.

Usage:
  python scripts/validate_visual_contract.py assets/example-visual-contract.json
  python scripts/validate_visual_contract.py lessons/my-review.json --require-reviewed

Normal PASS = structural plan is complete, NOT visual success.
Strict PASS requires review status/evidence files, but manual visual judging is
still essential.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FRAMES = [0, 25, 50, 75, 100]
KINDS = {"angles", "handoff", "interaction", "parameter_cases"}
VIEWPORTS = {"desktop", "mobile"}


def validate(data, base_dir=None, require_reviewed=False):
    errs = []
    warnings = []
    quantities = data.get("quantity_ids")
    anchors = data.get("anchor_ids")
    if not isinstance(quantities, list) or not quantities:
        return ["quantity_ids must be a nonempty array"], []
    if len(quantities) != len(set(quantities)):
        errs.append("duplicate quantity_ids")
    ids = set(quantities)
    if not isinstance(anchors, list) or not anchors:
        return ["anchor_ids must be a nonempty array"], []
    anchor_set = set(anchors)

    angles = data.get("angles", [])
    if not isinstance(angles, list):
        errs.append("angles must be an array")
        angles = []
    if data.get("requires_angles") is True and not angles:
        errs.append("this task requires angles, but none were specified")
    angle_ids = set()
    for a in angles:
        if not isinstance(a, dict):
            errs.append("angle item is not an object")
            continue
        aid = a.get("id")
        if aid in angle_ids:
            errs.append(f"duplicate angle {aid}")
        angle_ids.add(aid)
        for k in ("id", "ray_a", "ray_b", "anchor", "plane", "arc_id", "formula"):
            if not a.get(k):
                errs.append(f"angle {aid}: missing {k}")
        for k in ("id", "ray_a", "ray_b"):
            if a.get(k) not in ids:
                errs.append(f"angle {aid}: {k} not in quantity_ids")
        if a.get("ray_a") == a.get("ray_b"):
            errs.append(f"angle {aid}: the two rays are identical IDs")
        if a.get("anchor") not in anchor_set:
            errs.append(f"angle {aid}: anchor not in anchor_ids")
        if a.get("on_model") is not True:
            errs.append(f"angle {aid}: on_model must be true, label-only is insufficient")
        if a.get("world_rays") is not True:
            errs.append(f"angle {aid}: world_rays must be true")
        if a.get("inset") is True and a.get("inset_linked_to_anchor") is not True:
            errs.append(f"angle {aid}: inset must be linked to original anchor")
        if a.get("angle_exaggerated") is True and not a.get("exaggeration_label"):
            errs.append(f"angle {aid}: exaggerated angle needs visible disclaimer")

    stages = data.get("stages", [])
    if not isinstance(stages, list) or not stages:
        errs.append("stages must be a nonempty array")
        stages = []
    stage_lookup = {}
    for s in stages:
        if not isinstance(s, dict):
            errs.append("stage is not an object")
            continue
        n = s.get("step")
        if not isinstance(n, int) or n < 1 or n in stage_lookup:
            errs.append(f"invalid or duplicate stage step {n!r}")
            continue
        stage_lookup[n] = s
        for field in ("visible", "introduced", "retained"):
            values = s.get(field)
            if not isinstance(values, list):
                errs.append(f"stage {n}: missing {field} list")
                values = []
            for q in values:
                if q not in ids:
                    errs.append(f"stage {n}: unknown {field} quantity {q}")
        current_visible = set(s.get("visible", [])) if isinstance(s.get("visible"), list) else set()
        current_intro = set(s.get("introduced", [])) if isinstance(s.get("introduced"), list) else set()
        current_retained = set(s.get("retained", [])) if isinstance(s.get("retained"), list) else set()
        if not current_intro.issubset(current_visible):
            errs.append(f"stage {n}: newly introduced quantities must be visible")
        if not current_retained.issubset(current_visible):
            errs.append(f"stage {n}: retained quantities must be visible")

    handoffs = data.get("handoffs", [])
    if not isinstance(handoffs, list):
        errs.append("handoffs must be an array")
        handoffs = []
    if len(stage_lookup) > 1 and not handoffs:
        errs.append("multi-step lessons must document adjacent-step handoffs")
    covered_pairs=set()
    for h in handoffs:
        if not isinstance(h, dict):
            errs.append("handoff is not an object")
            continue
        f, t = h.get("from_step"), h.get("to_step")
        title = f"{f}->{t}"
        if not isinstance(f, int) or not isinstance(t, int) or t != f+1:
            errs.append(f"{title}: handoff must describe consecutive UI steps")
        elif (f,t) in covered_pairs:
            errs.append(f"{title}: duplicate handoff")
        else:
            covered_pairs.add((f,t))
        if f not in stage_lookup or t not in stage_lookup:
            errs.append(f"{title}: missing source or destination stage definition")
            continue
        old, new = stage_lookup[f], stage_lookup[t]
        r, n = h.get("retained"), h.get("introduced")
        if not isinstance(r, list) or not r:
            errs.append(f"{title}: missing retained IDs")
            r=[]
        if not isinstance(n, list) or not n:
            errs.append(f"{title}: missing introduced IDs")
            n=[]
        if not set(r).issubset(set(old.get("visible", [])) & set(new.get("visible", []))):
            errs.append(f"{title}: retained IDs must appear in BOTH steps' visible geometry")
        if not set(r).issubset(set(new.get("retained", []))):
            errs.append(f"{title}: next stage must declare retained IDs")
        if not set(n).issubset(set(new.get("introduced", []))):
            errs.append(f"{title}: introduced IDs must be NEW in next stage")
        if set(n) & set(old.get("visible", [])):
            errs.append(f"{title}: new IDs already visible in previous step")
        if h.get("frames") != FRAMES:
            errs.append(f"{title}: require exactly keyframes {FRAMES}")
        if not h.get("operation") or not h.get("visual_proof"):
            errs.append(f"{title}: must name physical operation and visual proof")
        relationship=h.get("source_relationship")
        if relationship not in {"derived","copied","transformed","recombined","new-input"}:
            errs.append(f"{title}: invalid source_relationship")
        if relationship != "new-input" and h.get("source_identity") not in ids:
            errs.append(f"{title}: source_identity must reference a quantity ID")
        if relationship == "copied" and h.get("same_input") is not True:
            errs.append(f"{title}: copied input must preserve source identity")
    ordered_steps=sorted(stage_lookup)
    for a,b in zip(ordered_steps,ordered_steps[1:]):
        if b!=a+1:
            errs.append(f"missing UI step(s) between {a} and {b}")
        elif (a,b) not in covered_pairs:
            errs.append(f"missing handoff specification {a}->{b}")

    checks = data.get("checks", [])
    if not isinstance(checks, list):
        errs.append("checks must be a list")
        checks = []
    seen_kinds = set()
    for ck in checks:
        if not isinstance(ck, dict):
            errs.append("check is not an object")
            continue
        kind = ck.get("kind")
        seen_kinds.add(kind)
        if kind not in KINDS:
            errs.append(f"unknown check kind {kind}")
        if not VIEWPORTS.issubset(set(ck.get("viewports", []))):
            errs.append(f"check {kind}: must cover desktop AND mobile")
        if kind in {"angles", "handoff"} and ck.get("frames") != FRAMES:
            errs.append(f"check {kind}: require keyframes {FRAMES}")
        status=ck.get("review_status", "pending")
        if status not in ("pending", "pass", "fail"):
            errs.append(f"check {kind}: invalid review_status")
        if require_reviewed:
            if status != "pass":
                errs.append(f"check {kind}: manual review not PASS")
            notes=ck.get("review_notes","")
            if not isinstance(notes,str) or len(notes.strip()) < 16:
                errs.append(f"check {kind}: missing meaningful reviewer notes")
            shots=ck.get("screenshots",[])
            if not isinstance(shots,list) or not shots:
                errs.append(f"check {kind}: missing screenshot evidence")
            else:
                for file in shots:
                    if not isinstance(file,str) or not (base_dir/str(file)).is_file():
                        errs.append(f"check {kind}: screenshot not found: {file}")
        elif status != "pass":
            warnings.append(f"{kind}: review is {status} (no visual pass claimed)")
    required_kinds={"parameter_cases"}
    if len(stage_lookup)>1:
        required_kinds.add("handoff")
    if angles:
        required_kinds.add("angles")
    if data.get("requires_interaction",True):
        required_kinds.add("interaction")
    for kind in sorted(required_kinds-seen_kinds):
        errs.append(f"missing check kind: {kind}")
    return errs, warnings


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest",type=Path)
    ap.add_argument("--require-reviewed",action="store_true")
    ns=ap.parse_args()
    try:
        data=json.loads(ns.manifest.read_text(encoding="utf-8"))
    except (OSError,ValueError) as e:
        print(f"FAIL: cannot read manifest: {e}")
        return 2
    errs, warnings=validate(data, ns.manifest.resolve().parent, ns.require_reviewed)
    for e in errs: print("FAIL:",e)
    if errs:
        print(f"FAIL: {len(errs)} visual-contract issue(s)")
        return 1
    print("PASS: angle-ray identity and adjacent-step STRUCTURAL contracts")
    for w in warnings: print("PENDING:",w)
    print("IMPORTANT: no script can prove the learner can identify the actual two rays; inspect the screenshots.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
