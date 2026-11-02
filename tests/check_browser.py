"""Visual/title regression smoke test against the real aiohttp server.
Requires playwright and its Chromium browser. Captures screenshots and a short
video so the character motion can be inspected rather than judged from a still.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ORIGIN="http://127.0.0.1:8765"
ART=Path("artifacts/browser")
ART.mkdir(parents=True,exist_ok=True)

async def inspect_page(browser,label,viewport,mobile=False):
    context=await browser.new_context(
        viewport=viewport,
        device_scale_factor=1,
        is_mobile=mobile,
        has_touch=mobile,
        record_video_dir=str(ART/"video"),
        record_video_size={"width":viewport["width"],"height":viewport["height"]})
    page=await context.new_page()
    errors=[]
    page.on("pageerror",lambda error: errors.append(str(error)))
    response=await page.goto(ORIGIN,wait_until="domcontentloaded")
    assert response.status==200, (label,response.status)
    await page.wait_for_function(
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/title_layers/background.webp'",
        timeout=20000
    )
    loaded=await page.evaluate("""() => ({
      ok: typeof originalTitleLayers !== 'undefined' && !!originalTitleLayers,
      actors: typeof originalTitleLayers !== 'undefined' && originalTitleLayers?.length,
      background: document.getElementById('homeCoverArt').naturalWidth,
      visible: getComputedStyle(document.getElementById('home')).display !== 'none'
    })""")
    assert loaded["ok"] and loaded["actors"]==4, (label,loaded)
    assert loaded["background"]==1672, (label,loaded)
    assert loaded["visible"],label
    await page.wait_for_timeout(350)
    previous=await page.locator("#weather").evaluate(
        "(canvas) => Array.from(canvas.getContext('2d').getImageData(160,550,100,100).data).filter((v,i)=>i%4===3&&v>0).length"
    )
    assert previous>300,label+" hero alpha mask did not render"
    await page.screenshot(path=str(ART/(label+".png")),full_page=True)
    await page.wait_for_timeout(550)
    await page.emulate_media(reduced_motion="reduce")
    await page.wait_for_function(
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/portada.webp'",
        timeout=5000
    )
    await page.emulate_media(reduced_motion="no-preference")
    await page.wait_for_function(
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/title_layers/background.webp'",
        timeout=5000
    )
    assert not errors,(label,errors)
    await context.close()
    print("VISUAL PASS",label,loaded,"hero pixels",previous)

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        try:
            await inspect_page(browser,"desktop",{"width":1366,"height":768})
            await inspect_page(browser,"mobile",{"width":390,"height":844},True)
        finally:
            await browser.close()

if __name__=="__main__":
    asyncio.run(main())
