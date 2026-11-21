import streamlit as st

BASE_CSS = """
<style>
:root{--navy:#0B3D91;--navy-dark:#082B66;--green:#1B7F4B;--soft:#EEF4FB;--ink:#10233F;--line:#D5E1F2;}
html,body,.stApp{font-family:"Segoe UI","Noto Sans","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Telugu","Noto Sans Bengali",system-ui,sans-serif;color:var(--ink);}
.stApp{background:linear-gradient(180deg,#F6FAFF 0%,#FFFFFF 340px);}
[data-testid="stSidebar"]{background:var(--soft);border-right:1px solid var(--line);}
.brand{font-size:1.45rem;font-weight:700;color:var(--navy);line-height:1.2;margin-bottom:.1rem;}
.brand span{color:var(--green);}
.tag{font-size:.9rem;color:#3C5578;margin-bottom:.8rem;}
.hero{background:linear-gradient(120deg,var(--navy) 0%,#14589F 100%);color:#fff;border-radius:18px;padding:2rem 2.2rem;margin-bottom:1.1rem;box-shadow:0 6px 20px rgba(11,61,145,.18);}
.hero h1{color:#fff;font-size:2.1rem;line-height:1.25;margin:0 0 .6rem 0;padding:0;}
.hero p{font-size:1.1rem;margin:0;max-width:62ch;color:#E8F0FF;}
.hero .motto{margin-top:.8rem;font-weight:600;color:#BDEBD0;}
.fcard{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1rem 1.1rem;height:100%;box-shadow:0 2px 8px rgba(16,35,63,.06);margin-bottom:.8rem;}
.fcard h4{margin:.2rem 0 .3rem 0;color:var(--navy);font-size:1.05rem;}
.fcard p{margin:0;font-size:.95rem;color:#33496B;}
.senior{background:#E9F6EF;border:1px solid #BFE3CF;border-left:6px solid var(--green);border-radius:12px;padding:1rem 1.2rem;margin:.6rem 0 1rem 0;}
.badge{display:inline-block;padding:.18rem .7rem;border-radius:999px;font-size:.85rem;font-weight:600;margin-right:.4rem;border:1px solid transparent;}
.badge.ok{background:#E3F5EA;color:#14693D;border-color:#B7E0C7;}
.badge.warn{background:#FFF4D9;color:#7A5200;border-color:#F1DB9A;}
.badge.no{background:#FDE8E8;color:#8F1D1D;border-color:#F3BDBD;}
.badge.info{background:#E4EEFC;color:var(--navy);border-color:#BED2F2;}
.sname{font-size:1.25rem;font-weight:700;color:var(--navy);margin:.2rem 0;}
.meta{font-size:.88rem;color:#4A6285;}
.stButton>button,.stLinkButton>a,.stFormSubmitButton>button{width:100%;border-radius:10px;font-weight:600;min-height:2.6rem;}
div[data-testid="stExpander"]{border-radius:12px;border:1px solid var(--line);background:#fff;}
div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px;}
.disc{font-size:.85rem;color:#4A6285;border-top:1px solid var(--line);padding-top:.5rem;margin-top:.6rem;}
:focus-visible{outline:3px solid #F5A400 !important;outline-offset:2px;}
@media (max-width:700px){.hero{padding:1.3rem 1.2rem}.hero h1{font-size:1.55rem}}
</style>
"""

SENIOR_CSS = """
<style>
html,body,.stApp,.stMarkdown,p,li,label,input,textarea,select,[data-baseweb]{font-size:1.28rem !important;line-height:1.6 !important;}
h1{font-size:2.3rem !important}h2{font-size:1.9rem !important}h3{font-size:1.6rem !important}
.stApp{background:#fff !important;color:#000 !important;}
.stButton>button,.stLinkButton>a,.stFormSubmitButton>button{min-height:3.6rem;font-size:1.3rem !important;border:2px solid var(--navy);}
.badge{font-size:1.05rem}.meta,.fcard p,.disc{font-size:1.1rem !important;color:#000 !important}
audio{width:100%;height:56px;}
</style>
"""


def inject(senior: bool) -> None:
    st.markdown(BASE_CSS + (SENIOR_CSS if senior else ""), unsafe_allow_html=True)
