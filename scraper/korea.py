import re, requests
from .skills import extract_skills, extract_responsibilities

H = {"User-Agent": "Mozilla/5.0 (personal research script)"}


def flatten(o):
    if isinstance(o, str):
        yield re.sub(r"<[^>]+>", "\n", o).replace("&nbsp;", " ")
    elif isinstance(o, dict):
        for v in o.values():
            yield from flatten(v)
    elif isinstance(o, list):
        for v in o:
            yield from flatten(v)


def make(company, url, item, title):
    text = "\n".join(flatten(item))
    return dict(source=company.lower(), company=company, country="KR", url=url, title=title,
                skills=extract_skills(text), responsibilities=extract_responsibilities(text))


def kakao():
    out, page = [], 1
    while page <= 10:
        r = requests.get("https://careers.kakao.com/public/api/job-list",
                         params=dict(skillSet="", part="TECHNOLOGY", company="ALL", keyword="",
                                     employeeType="", page=page), headers=H, timeout=30)
        r.raise_for_status()
        d = r.json()
        for it in d.get("jobList", []):
            rid = it.get("realId") or it.get("jobOfferId")
            out.append(make("Kakao", f"https://careers.kakao.com/jobs/{rid}", it,
                            it.get("jobOfferTitle", "")))
        if page >= int(d.get("totalPage", 1)):
            break
        page += 1
    return out


def toss():
    r = requests.get("https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs", headers=H, timeout=30)
    r.raise_for_status()
    d = r.json()
    items = d.get("success", d) if isinstance(d, dict) else d
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        out.append(make("Toss", f"https://toss.im/career/job-detail?job_id={it.get('id')}", it,
                        it.get("title", "")))
    return out


def woowa():
    r = requests.get("https://career.woowahan.com/w1/recruits",
                     params=dict(category="jobGroupCodes:BA005001", recruitCampaignSeq=0,
                                 jobGroupCodes="BA005001", page=0, size=200),
                     headers=H, timeout=30)
    r.raise_for_status()
    items = r.json().get("data", {}).get("list", [])
    return [make("Woowa", f"https://career.woowahan.com/recruitment/{it.get('recruitNumber')}/detail",
                 it, it.get("recruitName", "")) for it in items]


def fetch():
    out = []
    for fn in (kakao, toss, woowa):
        try:
            res = fn()
            print(fn.__name__, "->", len(res))
            out += res
        except Exception as e:
            print(fn.__name__, "FAILED:", repr(e))
    return out
