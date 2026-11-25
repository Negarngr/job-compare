import re
from playwright.sync_api import sync_playwright
from .skills import extract_skills, extract_responsibilities

# بعداً اگر لازم شد این آدرس را با آدرس واقعی جستجوی «اسنپ» در جاب‌ویژن عوض می‌کنیم
SEARCH_URLS = ["https://jobvision.ir/jobs/keyword/اسنپ"]
COMPANY_RX = re.compile(r"اسنپ|snapp", re.I)
TECH_RX = re.compile(r"developer|engineer|devops|data|\bml\b|\bqa\b|backend|frontend|android|ios|"
                     r"برنامه.?نویس|توسعه.?دهنده|مهندس|داده|دواپس|تحلیلگر", re.I)


def fetch():
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(locale="fa-IR")
        links = set()
        for url in SEARCH_URLS:
            page.goto(url, wait_until="networkidle", timeout=60000)
            for _ in range(8):
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(800)
            hrefs = page.eval_on_selector_all("a[href*='/jobs/']", "e=>e.map(x=>x.href)")
            links |= {h.split("?")[0] for h in hrefs if re.search(r"/jobs/\d+", h)}
        print("links found:", len(links))
        for link in links:
            try:
                page.goto(link, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(1000)
                title = page.locator("h1").first.inner_text().strip()
                text = page.inner_text("body")
            except Exception as e:
                print("skip", link, e)
                continue
            if not COMPANY_RX.search(text[:3000]) or not TECH_RX.search(title):
                continue
            out.append(dict(source="jobvision", company="Snapp", country="IR", url=link,
                            title=title, skills=extract_skills(text),
                            responsibilities=extract_responsibilities(text)))
            page.wait_for_timeout(1500)
        b.close()
    print("jobvision jobs:", len(out))
    return out
