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
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/title_layers/background_hd.webp'",
        timeout=20000
    )
    loaded=await page.evaluate("""() => ({
      ok: typeof originalTitleLayers !== 'undefined' && !!originalTitleLayers,
      actors: typeof originalTitleLayers !== 'undefined' && originalTitleLayers?.length,
      background: document.getElementById('homeCoverArt').naturalWidth,
      visible: getComputedStyle(document.getElementById('home')).display !== 'none'
    })""")
    assert loaded["ok"] and loaded["actors"]==4, (label,loaded)
    assert loaded["background"]==3344, (label,loaded)
    assert loaded["visible"],label
    # Compare deterministic instants with environmental particles removed.
    # This proves character layers move, rather than merely foliage drifting.
    moved=await page.evaluate("""() => {
      const ctx=document.getElementById('weather').getContext('2d');
      const boxes=[[0,493,298,297],[228,509,275,305],
                   [1213,84,205,131],[1425,509,176,208]];
      const capture=(t)=>{
        ctx.clearRect(0,0,1672,941);
        drawOriginalTitleCharacters(t);
        return boxes.map(([x,y,w,h])=>ctx.getImageData(x,y,w,h).data);
      };
      const first=capture(0),second=capture(2.7);
      return first.map((data,i)=>{
        let changed=0;
        for(let k=0;k<data.length;k+=4)
          if(Math.abs(data[k]-second[i][k])+
             Math.abs(data[k+1]-second[i][k+1])+
             Math.abs(data[k+2]-second[i][k+2])+
             Math.abs(data[k+3]-second[i][k+3])>32)changed++;
        return changed;
      });
    }""")
    assert all(count>100 for count in moved),(label,"missing character movement",moved)
    print("TITLE MOTION VERIFIED",label,moved)
    await page.wait_for_timeout(350)
    previous=await page.locator("#weather").evaluate(
        "(canvas) => Array.from(canvas.getContext('2d').getImageData(160,550,100,100).data).filter((v,i)=>i%4===3&&v>0).length"
    )
    assert previous>300,label+" hero alpha mask did not render"
    await page.screenshot(path=str(ART/(label+".png")),full_page=True)
    await page.wait_for_timeout(550)
    await page.emulate_media(reduced_motion="reduce")
    await page.wait_for_function(
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/portada_hd.webp'",
        timeout=5000
    )
    await page.emulate_media(reduced_motion="no-preference")
    await page.wait_for_function(
        "() => document.querySelector('#homeCoverArt')?.getAttribute('src') === '/assets/title_layers/background_hd.webp'",
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
