#!/usr/bin/env python3
"""Capture REAL desktop/mobile keyframes through an explicit test hook.

Optional dependency: Playwright with Chromium.
Required HTML interface:
window.lessonTest = {
 setStep(stepNumber) {...},       // 1-based UI step
 setPhase(fraction) {...},        // progress 0..1 inside step
 setView(name) {...},             // required for extra views
 getEvidence() {...}             // optional serializable quantity state
};
Capture success != human readability pass.
"""
from __future__ import annotations
import argparse
import asyncio
from html import escape
from pathlib import Path


async def capture(html_path, out_dir, stages, views, selector, chromium_executable=None):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("FAIL: Playwright not installed; this visual check was NOT RUN.")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    records,errors=[],[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True, executable_path=chromium_executable)
        try:
            for name,width,height in (("desktop",1280,800),("mobile",390,844)):
                page=await browser.new_page(viewport={"width":width,"height":height})
                page.on("pageerror",lambda exc: errors.append(str(exc)))
                await page.set_content(html_path.read_text(encoding="utf-8"),wait_until="domcontentloaded")
                ok=await page.evaluate("""() => !!(window.lessonTest &&
                    typeof window.lessonTest.setStep==='function' &&
                    typeof window.lessonTest.setPhase==='function')""")
                if not ok:
                    errors.append(f"{name}: missing lessonTest.setStep/setPhase interface")
                    await page.close()
                    continue
                for step in stages:
                    for view in views:
                        for phase in (0,.25,.5,.75,1):
                            try:
                                await page.evaluate("""({step,phase,view}) => {
                                   window.lessonTest.setStep(step);
                                   window.lessonTest.setPhase(phase);
                                   if(view!=='default') {
                                     if(typeof window.lessonTest.setView!=='function')
                                       throw Error('lessonTest.setView missing');
                                     window.lessonTest.setView(view);
                                   }
                                }""", {"step":step,"phase":phase,"view":view})
                                await page.wait_for_timeout(80)
                                fname=f"{name}_step{step:02}_p{round(phase*100):03}_{view}.png"
                                dest=out_dir/fname
                                if selector:
                                    element=page.locator(selector)
                                    if await element.count()==0:
                                        raise RuntimeError(f"selector not found: {selector}")
                                    await element.first.screenshot(path=str(dest))
                                else:
                                    await page.screenshot(path=str(dest),full_page=False)
                                records.append((name,step,phase,view,fname))
                            except Exception as exc:
                                errors.append(f"{name}/step{step}/{phase}/{view}: {exc}")
                await page.close()
        finally:
            await browser.close()
    html = """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>关键帧视觉人工复核</title>
<style>body{font:14px system-ui;background:#f3f5f7;color:#223;padding:20px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:15px}
figure{margin:0;background:#fff;padding:9px;border:1px solid #ccd;border-radius:10px}
img{max-width:100%;display:block;border-radius:7px}
figcaption{padding:9px 3px}</style>
<h1>关键帧：人工复核</h1><p>检查原位角两条边、连续交接、手机遮挡。
截图存在不等于看得懂。</p><main>"""
    for name,step,phase,view,fname in records:
        html+=f'<figure><img src="{escape(fname)}"><figcaption>{name} / 第{step}步 / {phase:.0%} / {escape(view)}</figcaption></figure>'
    html+="</main></html>"
    (out_dir/"index.html").write_text(html,encoding="utf-8")
    print(f"Captured: {len(records)} screenshots; gallery: {out_dir/'index.html'}")
    for error in errors: print("FAIL:",error)
    if errors:
        print("NOT APPROVED: browser capture failures; no readability claim")
        return 1
    print("PASS: screenshot capture only (human visual review still required)")
    return 0


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html",type=Path)
    ap.add_argument("--out",type=Path,default=Path("review_frames"))
    ap.add_argument("--stages",default="5,6")
    ap.add_argument("--views",default="default")
    ap.add_argument("--selector",default=None)
    ap.add_argument("--chromium-executable",default=None,help="optional local Chromium path")
    args=ap.parse_args()
    if not args.html.is_file():
        ap.error(f"HTML not found: {args.html}")
    steps=[int(x) for x in args.stages.split(",") if x.strip()]
    views=[x.strip() for x in args.views.split(",") if x.strip()]
    if not steps or not views or any(i<=0 for i in steps):
        ap.error("require positive 1-based steps and nonempty view names")
    return asyncio.run(capture(args.html,args.out,steps,views,args.selector,args.chromium_executable))


if __name__=="__main__":
    raise SystemExit(main())
