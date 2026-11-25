import os, json, sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from scraper.skills import SKILLS

st.set_page_config(page_title="Snapp vs Korea", layout="centered")
st.title("🇮🇷 اسنپ vs 🇰🇷 کره")

if not os.path.exists("data/jobs.db"):
    st.info("هنوز داده‌ای جمع نشده. اول باید workflow در GitHub یک بار اجرا شود.")
    st.stop()

df = pd.read_sql("SELECT * FROM jobs WHERE active=1", sqlite3.connect("data/jobs.db"))
if df.empty:
    st.info("آگهی فعالی وجود ندارد.")
    st.stop()

df["skills"] = df.skills.apply(json.loads)
df["responsibilities"] = df.responsibilities.apply(json.loads)

c1, c2 = st.columns(2)
c1.metric("آگهی اسنپ", int((df.country == "IR").sum()))
c2.metric("آگهی کره", int((df.country == "KR").sum()))


def share(country):
    d = df[df.country == country]
    n = max(len(d), 1)
    return pd.Series({s: sum(s in x for x in d.skills) / n * 100 for s in SKILLS})


cmp = pd.DataFrame({"Snapp": share("IR"), "Korea": share("KR")})
cmp["gap"] = cmp.Korea - cmp.Snapp
cmp["category"] = [SKILLS[s][0] for s in cmp.index]
cmp.index.name = "skill"

t1, t2, t3 = st.tabs(["مقایسه", "گپ مهارتی", "آگهی‌ها"])
with t1:
    cat = st.selectbox("دسته", ["همه"] + sorted(cmp.category.unique()))
    v = cmp if cat == "همه" else cmp[cmp.category == cat]
    fig = px.bar(v.reset_index(), y="skill", x=["Snapp", "Korea"], barmode="group",
                 orientation="h", labels={"value": "% آگهی‌ها", "variable": ""})
    st.plotly_chart(fig, use_container_width=True)
with t2:
    st.caption("مهارت‌هایی که در کره پرتقاضاترند ولی در اسنپ کمتر آمده")
    st.dataframe(cmp.sort_values("gap", ascending=False).head(10).round(1))
with t3:
    country = st.radio("کشور", ["IR", "KR"], horizontal=True)
    for _, r in df[df.country == country].iterrows():
        with st.expander(f"{r.company} — {r.title}"):
            st.write(", ".join(r.skills) or "—")
            for l in r.responsibilities:
                st.markdown(f"- {l}")
            st.link_button("باز کردن آگهی", r.url)
