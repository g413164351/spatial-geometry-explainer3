#!/usr/bin/env python3
"""Negative regression tests for generic visual quality contracts."""
import copy
import json
from pathlib import Path
from validate_visual_contract import validate

ROOT=Path(__file__).resolve().parent.parent


def expect_fail(data, label):
    problems, _ = validate(data, ROOT/"assets")
    assert problems, f"should FAIL for {label}, but did not"
    return problems


def main():
    plan=json.loads((ROOT/"assets/example-visual-contract.json").read_text(encoding="utf-8"))
    errors,_=validate(plan,ROOT/"assets")
    assert not errors, errors

    x=copy.deepcopy(plan)
    x["angles"][0]["ray_b"]=x["angles"][0]["ray_a"]
    expect_fail(x,"two angle edges with the same ID")

    x=copy.deepcopy(plan)
    x["angles"][0]["on_model"]=False
    expect_fail(x,"label-only angle")

    x=copy.deepcopy(plan)
    x["angles"][0]["inset_linked_to_anchor"]=False
    expect_fail(x,"unanchored enlargement")

    x=copy.deepcopy(plan)
    x["handoffs"][0]["retained"]=["u","theta"]
    x["stages"][1]["visible"]=["uAlong","uAcross"]
    expect_fail(x,"lost previous scene geometry")

    x=copy.deepcopy(plan)
    x["handoffs"][0]["frames"]=[0,100]
    expect_fail(x,"transition frames omitted")

    x=copy.deepcopy(plan)
    x["handoffs"][0]["to_step"]=5
    expect_fail(x,"nonadjacent step mapping")

    x=copy.deepcopy(plan)
    x["handoffs"][0]["source_relationship"]="copied"
    x["handoffs"][0]["same_input"]=False
    expect_fail(x,"copied vector identity not preserved")

    x=copy.deepcopy(plan)
    x["handoffs"]=[]
    expect_fail(x,"missing adjacent handoff")

    strict,_=validate(copy.deepcopy(plan),ROOT/"assets",require_reviewed=True)
    assert strict, "pending example must never get strict PASS"

    # General-use check: no angle needed for every type of diagram.
    no_angle=copy.deepcopy(plan)
    no_angle["requires_angles"]=False
    no_angle["angles"]=[]
    no_angle["checks"]=[c for c in no_angle["checks"] if c["kind"]!="angles"]
    assert not validate(no_angle,ROOT/"assets")[0], "non-angle tasks must be allowed"

    print("PASS: rejects absent angle edges, label-only annotations, orphan insets")
    print("PASS: rejects lost provenance, missing keyframes, nonadjacent steps")
    print("PASS: rejects missing handoff and failed copy-identity conservation")
    print("PASS: pending visual reviews fail strict mode; non-angle tasks allowed")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
