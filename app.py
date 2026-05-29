#!/usr/bin/env python3
"""
Job Automation Studio
A no-code tool to generate personalised job application automation scripts.

Run:  python app.py
No terminal skills needed — just answer the questions!

Requirements: pip install gradio PyYAML
"""

import gradio as gr
import json
import time
import random
import re
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

JOB_SITES_INFO = {
    "LinkedIn": {
        "url": "linkedin.com",
        "easy_apply": True,
        "notes": "Best for automation (Easy Apply). Watch for error_code:9101 anti-bot.",
    },
    "Indeed": {
        "url": "indeed.com",
        "easy_apply": True,
        "notes": "Direct apply. Less strict on bots.",
    },
    "Glassdoor": {
        "url": "glassdoor.com",
        "easy_apply": False,
        "notes": "Company reviews + jobs. Best used manually.",
    },
    "Jobstreet ID": {
        "url": "jobstreet.co.id",
        "easy_apply": True,
        "notes": "Popular in Indonesia. Good for local jobs.",
    },
    "Glints": {
        "url": "glints.com",
        "easy_apply": True,
        "notes": "Tech jobs in Indonesia. Also great for recruiter outreach.",
    },
    "AngelList": {
        "url": "angel.co",
        "easy_apply": True,
        "notes": "Startups. Remote-friendly. Salaries are shown.",
    },
    "WeWorkRemotely": {
        "url": "weworkremotely.com",
        "easy_apply": False,
        "notes": "100% remote jobs. Very automation-friendly layout.",
    },
    "RemoteOK": {
        "url": "remoteok.com",
        "easy_apply": False,
        "notes": "Remote jobs aggregator. Simple layout.",
    },
}

LOCATION_PRESETS = {
    "🇮🇩 Indonesia — Karawang/Cikarang (on-site)": [
        "Karawang, Jawa Barat", "Cikarang, Jawa Barat", "Bekasi, Jawa Barat", "Purwakarta, Jawa Barat",
    ],
    "🇮🇩 Indonesia — Jakarta (hybrid/remote)": ["Jakarta, Indonesia"],
    "🇸🇬 Singapore (remote)": ["Singapore (Remote)"],
    "🇲🇾 Malaysia (remote)": ["Malaysia (Remote)"],
    "🇹🇭 Thailand (remote)": ["Thailand (Remote)"],
    "🌏 All locations above": [
        "Karawang, Jawa Barat", "Cikarang, Jawa Barat", "Bekasi, Jawa Barat",
        "Jakarta, Indonesia", "Singapore (Remote)", "Malaysia (Remote)", "Thailand (Remote)",
    ],
}

WORK_TYPES = [
    ("Remote only", "I only want remote jobs"),
    ("Hybrid preferred", "Remote is ideal, but hybrid is OK"),
    ("On-site OK", "I'm fine with any location near me"),
    ("No preference", "Any work type — just give me a job!"),
]

SENIORITY_OPTIONS = [
    ("Entry / Junior only", "Skip anything Senior, Lead, Manager, Director"),
    ("Mid-level OK", "Junior and Mid-level are fine"),
    ("Senior OK", "I'm happy with senior roles too"),
]

PRESETS = {
    "🎯 Custom (tell us everything)": "custom",
    "💻 Developer (MERN / Next.js)": "fullstack",
    "🖥️ IT Support / Helpdesk": "it_support",
    "☁️ DevOps / Cloud Engineer": "devops",
    "📊 Data Analyst": "data_analyst",
    "🎨 UI/UX Designer": "designer",
    "📦 Fresh Graduate (any tech)": "freshgrad",
}

COVER_TONES = [
    ("Professional ✨", "Professional", "Clean and formal"),
    ("Friendly 😊", "Friendly", "Warm and approachable"),
    ("Direct ⚡", "Direct", "Short and to the point"),
]

TOOL_CHOICES = [
    ("🤖 OpenClaw / QClaw (Recommended — AI-powered)", "agent-browser",
     "Best option. The AI handles anti-bot, form filling, and errors automatically."),
    ("🖥️ Playwright (free, no AI)", "playwright",
     "Reliable browser automation. Needs some setup. No AI smarts though."),
    ("🌐 Selenium (classic)", "selenium",
     "Widely known. More setup than Playwright. Good for developers."),
    ("🤲 Manual (safest)", "manual",
     "Use the generated search queries and apply by hand. Slowest but safest."),
]

AI_MODE_CHOICES = [
    ("Yes — I have an AI agent (QClaw/OpenClaw/Claude)", True,
     "The script will delegate form filling and error handling to your AI agent."),
    ("No — just generate the queries", False,
     "We'll give you ready-to-use search URLs. You apply manually."),
]


def build_url(site: str, role: str, location: str) -> str:
    re = role.replace(" ", "+")
    lo = location.replace(",", "%2C").replace(" ", "+")
    table = {
        "LinkedIn":       f"https://www.linkedin.com/jobs/search/?keywords={re}&location={lo}&f_AL=true",
        "Indeed":         f"https://www.indeed.com/jobs?q={re}&l={lo}",
        "Glassdoor":      f"https://www.glassdoor.com/Search/results.htm?keyword={re}&loc={lo}",
        "Jobstreet ID":   f"https://www.jobstreet.co.id/id/job-search?keywords={re}&locations={location}",
        "Glints":         f"https://glints.com/lowongan-kerja/?keywords={re}",
        "AngelList":      f"https://angel.co/jobs?keywords={re}",
        "WeWorkRemotely": "https://weworkremotely.com",
        "RemoteOK":       "https://remoteok.com",
    }
    return table.get(site, f"https://www.google.com/search?q={re}+jobs+{lo}")


def extract_skills(text: str) -> list:
    keywords = [
        "python", "javascript", "typescript", "react", "vue", "angular", "node.js",
        "express", "fastapi", "django", "flask", "sql", "postgresql", "mysql",
        "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure",
        "git", "linux", "windows server", "networking", "security", "devops",
        "ci/cd", "jenkins", "github actions", "agile", "scrum", "jira",
        "microservices", "api", "rest", "graphql", "html", "css", "tailwind",
        "pandas", "numpy", "excel", "tableau", "power bi", "data analysis",
        "machine learning", "nlp", "sap", "erp", "salesforce", "crm",
        "photoshop", "figma", "sketch", "ui/ux", "product management",
        "communication", "problem solving", "leadership", "teamwork",
        "fullstack", "frontend", "backend", "mobile", "ios", "android",
    ]
    found = [k for k in keywords if k.lower() in text.lower()]
    return found


def detect_experience(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["senior", "lead", "manager", "director", "10+ years"]):
        return "Senior / Lead"
    if any(k in t for k in ["3+ years", "5 years", "5+ years", "mid-level"]):
        return "Mid-level"
    return "Entry / Junior"


def is_banking(company: str) -> bool:
    c = company.lower()
    banking = ["bank", "bca", "bni", "bri", "mandiri", "cimb", "maybank",
               "ocbc", "uob", "dbs", "permata", "panin", "btn", "jago",
               "ovo", "dana", "gopay", "linkaja", "shopeepay", "fintech",
               "financial", "finance", "investment", "securities", "insurance"]
    return any(b in c for b in banking)


def is_senior(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in ["senior", "lead", "manager", "director",
                                  "vp", "principal", "supervisor", "chief"])


# ══════════════════════════════════════════════════════════════════════════════
# SCRIPT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_script(
    name, email, phone, role, locations, sites,
    exclusions, daily_cap, salary_local, salary_remote,
    seniority_skip, remote_only, tone, work_type,
    cv_skills, ai_mode, tool,
):
    locs_json  = json.dumps(locations, indent=2)
    sites_json = json.dumps(sites, indent=2)
    excl_json  = json.dumps([e.strip() for e in (exclusions or "").split(",") if e.strip()])
    skills_txt = ", ".join(cv_skills[:8]) if cv_skills else "Python, JavaScript, SQL"

    senior_filter = "True" if seniority_skip else "False"
    remote_filter = "True" if remote_only else "False"

    tone_open = {"Professional": "I am writing to express my strong interest in",
                  "Friendly":     "I'm really excited about the opportunity to join",
                  "Direct":       "I want to apply for"}
    tone_close = {"Professional": "Thank you for your time and consideration.",
                   "Friendly":     "Can't wait to hear from you!",
                   "Direct":        "Looking forward to your response."}
    to  = tone_open.get(tone, tone_open["Professional"])
    tc  = tone_close.get(tone, tone_close["Professional"])

    script = f'''#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║     JOB APPLICATION AUTOMATION SCRIPT                                ║
║     Generated by Job Automation Studio                               ║
║     Candidate: {name or "Your Name":<42}     ║
║     Role:      {role or "Your Target Role":<42}     ║
╚══════════════════════════════════════════════════════════════════════╝

⚠️  BEFORE YOU RUN — READ THIS!

This script was GENERATED based on your answers. To actually apply to jobs,
you need ONE of these:

  🤖 BEST: Run this with an AI agent (QClaw, OpenClaw, Claude)
    → The AI handles anti-bot blocks, form filling, and adapts to changes
    → Just say: "Run my LinkedIn automation script"

  🖥️  OK:  Run with Playwright or Selenium directly
    → Install the tool first (see ../TOOLS/setup-guide.md)

  🤲  SAFEST: Use the Search Query list we also gave you
    → Open each link in your browser and apply manually

COMMON ERRORS & FIXES:
  • error_code:9101 on LinkedIn  → Add 90-120s delay between applications
  • UI changed (buttons missing) → Re-generate the script from the dashboard
  • Captcha appeared             → Run during off-peak hours or use a VPN
  • Script stopped working       → Job sites often change — re-generate!

REQUIREMENTS:
  pip install gradio PyYAML   (for the dashboard)
  pip install playwright       (for direct Playwright mode)
  pip install selenium         (for Selenium mode)

Generated with: AI_MODE={str(ai_mode)} | TOOL={tool}
"""

import json, time, random, re
from pathlib import Path
from datetime import datetime

# ─── CONFIG (filled from your answers) ───────────────────────────────────────
CANDIDATE_NAME  = "{name or 'Your Name'}"
EMAIL           = "{email or 'your@email.com'}"
PHONE           = "{phone or '+62 xxx xxxx xxxx'}"
TARGET_ROLE     = "{role or 'Target Role'}"
WORK_TYPE       = "{work_type}"        # Remote / Hybrid / On-site
COVER_TONE      = "{tone}"             # Professional / Friendly / Direct
DAILY_CAP       = {daily_cap}

LOCATIONS       = {locs_json}
JOB_SITES       = {sites_json}
EXCLUDE         = {excl_json}
SKIP_SENIOR     = {senior_filter}      # Skip Senior/Lead/Manager/Director?
REMOTE_ONLY     = {remote_filter}     # Only apply to remote jobs?
SALARY_LOCAL    = "{salary_local}"
SALARY_REMOTE   = "{salary_remote}"

# ─── TRACKER ──────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
TRACKER  = DATA_DIR / "applied_ids.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_ids():
    if TRACKER.exists():
        return set(json.loads(TRACKER.read_text()).get("applied_ids", []))
    return set()

def save_ids(ids):
    TRACKER.write_text(json.dumps({{"applied_ids": list(ids)}}, indent=2))

applied_ids = load_ids()

# ─── FILTERS ──────────────────────────────────────────────────────────────────
BANKING = [
    "bank","bca","bni","bri","mandiri","cimb","maybank","ocbc","uob","dbs",
    "permata","panin","btn","jago","ovo","dana","gopay","linkaja","shopeepay",
    "fintech","financial","finance","investment","securities","insurance",
] + [e.lower() for e in EXCLUDE]

SENIOR_KW = [
    "senior","lead","manager","director","vp","principal",
    "supervisor","chief","head of","intern",
]

def is_banking(company: str) -> bool:
    c = company.lower()
    return any(b in c for b in BANKING)

def is_senior(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in SENIOR_KW)

def should_apply(title: str, company: str, is_remote: bool) -> bool:
    if is_senior(title) and SKIP_SENIOR:
        print(f"  ⛔ Skipped (senior): {{title}}")
        return False
    if is_banking(company):
        print(f"  ⛔ Skipped (banking/fintech): {{company}}")
        return False
    if REMOTE_ONLY and not is_remote:
        print(f"  ⛔ Skipped (not remote): {{title}}")
        return False
    return True

# ─── COVER LETTER ─────────────────────────────────────────────────────────────
def cover_letter(role: str, company: str) -> str:
    return (
        f"Dear Hiring Manager,\\n\\n"
        f"{to} the {{role}} position at {{company}}.\\n\\n"
        f"I bring hands-on experience in {{skills_txt}}. I am comfortable "
        f"working in a {{WORK_TYPE}} setting and I am eager to contribute "
        f"to your team.\\n\\n"
        f"My salary expectation is {{SALARY_LOCAL}} for local roles and "
        f"{{SALARY_REMOTE}} for remote positions outside Indonesia.\\n\\n"
        f"{{tc}}\\n\\nBest regards,\\n{{CANDIDATE_NAME}}\\n{{EMAIL}}"
    )

# ─── BROWSER AUTOMATION ───────────────────────────────────────────────────────
# CHOOSE YOUR TOOL:
#
# agent_browser()  ← USE WITH QCLAW/OPENCLAW (AI handles everything — BEST)
# playwright_fn()  ← Use Playwright directly (pip install playwright)
# selenium_fn()    ← Use Selenium (pip install selenium)

def agent_browser(cmd: str, timeout: int = 60) -> str:
    """Run an agent-browser command. Requires OpenClaw/QClaw installed."""
    import subprocess
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def playwright_fn():
    """Playwright example — install first: pip install playwright && playwright install"""
    # from playwright.sync_api import sync_playwright
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page    = browser.new_page()
    raise NotImplementedError("Install Playwright: pip install playwright")

def selenium_fn():
    """Selenium example — install first: pip install selenium"""
    # from selenium import webdriver
    # driver = webdriver.Chrome()
    raise NotImplementedError("Install Selenium: pip install selenium")

def human_delay(min_s=2.0, max_s=5.0):
    """Random delay to mimic human behaviour (anti-bot)."""
    time.sleep(random.uniform(min_s, max_s))

# ─── SEARCH URL BUILDER ───────────────────────────────────────────────────────
def build_url(site: str, role: str, location: str) -> str:
    re = role.replace(" ", "+")
    lo = location.replace(",", "%2C").replace(" ", "+")
    table = {{
        "LinkedIn":       f"https://www.linkedin.com/jobs/search/?keywords={{re}}&location={{lo}}&f_AL=true",
        "Indeed":         f"https://www.indeed.com/jobs?q={{re}}&l={{lo}}",
        "Glassdoor":      f"https://www.glassdoor.com/Search/results.htm?keyword={{re}}&loc={{lo}}",
        "Jobstreet ID":   f"https://www.jobstreet.co.id/id/job-search?keywords={{re}}&locations={{location}}",
        "Glints":         f"https://glints.com/lowongan-kerja/?keywords={{re}}",
        "AngelList":      f"https://angel.co/jobs?keywords={{re}}",
        "WeWorkRemotely": "https://weworkremotely.com",
        "RemoteOK":       "https://remoteok.com",
    }}
    return table.get(site, f"https://www.google.com/search?q={{re}}+jobs+{{lo}}")

# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\\n🚀 Starting: {{TARGET_ROLE}} — {{datetime.now().strftime('%Y-%m-%d %H:%M')}}")
    print(f"   Sites: {{', '.join(JOB_SITES)}}")
    print(f"   Locations: {{', '.join(LOCATIONS)}}")
    print(f"   Cap: {{DAILY_CAP}} jobs/day\\n")

    applied_today = 0

    for site in JOB_SITES:
        if applied_today >= DAILY_CAP:
            break
        for location in LOCATIONS:
            if applied_today >= DAILY_CAP:
                break

            url = build_url(site, TARGET_ROLE, location)
            print(f"[SEARCH] {{site}} | {{TARGET_ROLE}} @ {{location}}")
            print(f"         {{url}}")

            # ── AI AGENT INTEGRATION ──────────────────────────────────────────
            # With QClaw/OpenClaw: paste this into your AI chat:
            # "Run my LinkedIn automation. Open: {{url}}"
            # The AI will log in, find jobs, and apply automatically.
            #
            # Direct automation: uncomment below and use Playwright/Selenium
            #
            # from playwright.sync_api import sync_playwright
            # with sync_playwright() as p:
            #     page = p.chromium.launch(headless=True).new_page()
            #     page.goto(url)
            #     human_delay(3, 6)
            #     # ... form filling logic here ...
            #     applied_today += 1
            #
            # human_delay(random.uniform(45, 90))  # anti-bot cooldown

            applied_today += 1   # Remove this line when using real browser automation

    print(f"\\n✅ Done! Applied: {{applied_today}} today | Total tracked: {{len(applied_ids)}}")

if __name__ == "__main__":
    main()
'''
    return script


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE OUTPUT
# ══════════════════════════════════════════════════════════════════════════════

def generate_output(
    name, email, phone,
    role, preset,
    locations_checklist, work_type, seniority,
    sites_checklist, daily_cap, salary_local, salary_remote,
    exclusions, tone, ai_mode, tool,
    cv_upload, cv_text,
):
    # Resolve role
    preset_map = {
        "💻 Developer (MERN / Next.js)": "Fullstack Developer",
        "🖥️ IT Support / Helpdesk":       "IT Support",
        "☁️ DevOps / Cloud Engineer":     "DevOps Engineer",
        "📊 Data Analyst":                "Data Analyst",
        "🎨 UI/UX Designer":              "UI/UX Designer",
        "📦 Fresh Graduate (any tech)":  "Junior Developer",
    }
    if preset != "🎯 Custom (tell us everything)":
        role = preset_map.get(preset, role)

    # Locations
    flat_locs = []
    for group, locs in LOCATION_PRESETS.items():
        if group in (locations_checklist or []):
            flat_locs.extend(locs)

    # Sites
    selected_sites = [s for s in (sites_checklist or []) if s in JOB_SITES_INFO]
    if not selected_sites:
        selected_sites = ["LinkedIn"]

    # Skills
    cv_full = cv_text or ""
    if cv_upload:
        try:
            with open(cv_upload.name, "r", encoding="utf-8", errors="ignore") as f:
                cv_full = f.read()
        except Exception:
            pass
    skills = extract_skills(cv_full)

    # Profile summary
    exp = detect_experience(cv_full)
    summary = f"""**Your Profile** ✅
- Name: `{name or "Fill in Step 1"}`
- Role: **{role or "Select a preset or enter custom"}**
- Experience: `{exp}`
- Skills detected: `{", ".join(skills[:8]) if skills else "Upload CV to detect"}`
- Work type: `{work_type}`
- Sites: `{", ".join(selected_sites)}`
"""

    # Script
    script = generate_script(
        name, email, phone, role, flat_locs, selected_sites,
        exclusions, daily_cap, salary_local, salary_remote,
        seniority == "Entry / Junior only", work_type == "Remote only",
        tone, work_type, skills, ai_mode, tool,
    )

    # Cover letters per site
    cl_parts = []
    for site in selected_sites[:3]:
        cl = f'**{site} Cover Letter**\\n```\\n{cover_letter_picker(role, name, email, skills, work_type, salary_local, salary_remote, tone, site)}\\n```'
        cl_parts.append(cl)

    # Search URLs
    url_lines = []
    for site in selected_sites:
        for loc in flat_locs[:5]:
            url_lines.append(f"- [{site}] **{role}** @ **{loc}**\n  {build_url(site, role or "role", loc)}")
    urls_text = "\n".join(urls_text for urls_text in url_lines) if url_lines else "_Select locations in Step 2_"

    disclaimer = """⚠️ **Before you run this script — important:**

**🤖 Best result:** Open this in **QClaw or OpenClaw** and say:
> *"Run my job automation script"*

Your AI agent will handle the smart parts:
- Logging into LinkedIn / Indeed
- Filling forms with your details
- Handling `error_code:9101` anti-bot blocks
- Writing cover letters per job
- Skipping banks and senior roles automatically

**🖥️ Alternative:** Use `playwright` or `selenium` directly.
See `TOOLS/setup-guide.md` for installation.

**🤲 Simplest:** Just click the **Search URLs** below — they'll open in your browser. Apply manually.
"""

    return summary, script, "\n\n".join(cl_parts), urls_text, disclaimer


def cover_letter_picker(role, name, email, skills, work_type, sal_l, sal_r, tone, site):
    to  = {"Professional": "I am writing to express my strong interest in",
           "Friendly":     "I'm really excited about the opportunity to join",
           "Direct":        "I want to apply for"}.get(tone, "I am writing to apply for")
    tc  = {"Professional": "Thank you for your time.",
           "Friendly":     "Can't wait to hear from you!",
           "Direct":        "Looking forward to your response."}.get(tone, "Thank you.")
    sk  = ", ".join(skills[:6]) if skills else "relevant technical skills"
    nm  = name or "Your Name"
    return (f"{nm}\\n{email}\\n\\n{to} the {role} position at [Company Name].\\n\\n"
            f"I bring hands-on experience in {sk}. I'm comfortable working {work_type.lower()} "
            f"and am eager to contribute to your team.\\n\\n"
            f"Salary expectation: {sal_l} (local) / {sal_r} (remote outside Indonesia).\\n\\n"
            f"{tc}\\n\\n{nm}")


# ══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ══════════════════════════════════════════════════════════════════════════════

with gr.Blocks(
    title="Job Automation Studio",
    theme=gr.themes.Default(
        primary_hue="indigo",
        secondary_hue="violet",
    ),
    css="""
    .hero {
        text-align: center;
        padding: 28px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .hero h1 { font-size: 2em; margin: 0 0 8px; }
    .hero p  { font-size: 1.05em; opacity: 0.9; margin: 0; }
    .info-box  { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 8px; }
    .warn-box  { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 14px; border-radius: 8px; }
    .ok-box    { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 14px; border-radius: 8px; }
    .tab-title { font-size: 1.15em; font-weight: 700; color: #4f46e5; margin-bottom: 10px; }
    .section   { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
    """,
) as demo:

    gr.HTML("""<div class="hero">
        <h1>🚀 Job Automation Studio</h1>
        <p>Answer a few questions → Get your personalised job automation script.<br>
        No coding needed. Works best with AI agents (QClaw, OpenClaw, Claude).</p>
    </div>""")

    with gr.Tabs():

        # ════════════════════════════════════════════════════════════
        # TAB 1 — ABOUT YOU
        # ════════════════════════════════════════════════════════════
        with gr.Tab("📋 Step 1 — About You"):
            gr.Markdown("### Tell us about yourself")
            gr.Markdown("*All fields optional — the more you share, the better the script!*")

            with gr.Row():
                name_in  = gr.Textbox(label="Full Name",          placeholder="e.g. Muhamad Septian Pamungkas", lines=1)
                email_in = gr.Textbox(label="Email",              placeholder="your@email.com")
                phone_in = gr.Textbox(label="Phone / WhatsApp",   placeholder="+62 896 0247 5967")

            with gr.Row():
                cv_up = gr.File(label="📄 Upload CV (PDF/TXT) — auto-fills skills", file_types=[".pdf", ".txt"])
                cv_tx = gr.Textbox(label="…or paste CV text here", lines=5,
                                   placeholder="Paste your CV text here to extract skills automatically…")

            gr.Markdown("#### 🎯 What kind of work are you looking for?")
            preset_in = gr.Radio(
                choices=list(PRESETS.keys()),
                value="🎯 Custom (tell us everything)",
                label="Choose a preset (or custom)",
            )
            role_in = gr.Textbox(
                label="Job Title / Role",
                placeholder="e.g. Fullstack Developer, IT Support, Data Analyst…",
                lines=1,
            )

            profile_out = gr.Markdown("", visible=True)

            gr.Markdown("*Profile auto-summarised after you fill in above ↑*")

        # ════════════════════════════════════════════════════════════
        # TAB 2 — JOB PREFERENCES
        # ════════════════════════════════════════════════════════════
        with gr.Tab("🎯 Step 2 — Job Preferences"):

            gr.Markdown("#### 📍 Where do you want to work?")
            gr.Markdown("*Select all that apply. The script will search all these locations.*")
            locs_in = gr.CheckboxGroup(
                choices=list(LOCATION_PRESETS.keys()),
                value=["🇮🇩 Indonesia — Karawang/Cikarang (on-site)"],
                label="Location Groups",
            )

            gr.Markdown("#### 🏢 Work Type")
            wt_in = gr.Radio(
                choices=[v[1] for v in WORK_TYPES],
                value="Remote only",
                label="What work setup do you prefer?",
            )

            gr.Markdown("#### ⭐ Seniority Level")
            sr_in = gr.Radio(
                choices=[v[1] for v in SENIORITY_OPTIONS],
                value="Skip anything Senior, Lead, Manager, Director",
                label="What level roles do you want?",
            )

            gr.Markdown("#### 🏦 Companies to AVOID")
            excl_in = gr.Textbox(
                label="Companies to skip (comma-separated)",
                placeholder="e.g. Bank BCA, OVO, GoPay, DBS Bank…",
                lines=2,
                value="bank, fintech, ovo, dana, gopay, linkaja, shopeepay",
            )
            gr.Markdown("*Already pre-filled with common banking/fintech names. Add more!*")

            gr.Markdown("#### 💰 Salary Expectations (monthly)")
            with gr.Row():
                sal_l = gr.Textbox(
                    label="Local / Indonesia",
                    value="IDR 6,500,000",
                    placeholder="e.g. IDR 6,500,000",
                )
                sal_r = gr.Textbox(
                    label="Remote (outside Indonesia)",
                    value="USD 500",
                    placeholder="e.g. USD 500",
                )

            gr.Markdown("#### 🔢 Daily Application Cap")
            cap_in = gr.Slider(5, 100, value=50, step=5, label="Max jobs to apply per day",)

        # ════════════════════════════════════════════════════════════
        # TAB 3 — JOB SITES & TOOLS
        # ════════════════════════════════════════════════════════════
        with gr.Tab("🌐 Step 3 — Job Sites & Tools"):

            gr.Markdown("#### 🌐 Which job sites do you want to search?")
            gr.Markdown("*The script will search ALL selected sites. More sites = more jobs.*")
            sites_in = gr.CheckboxGroup(
                choices=list(JOB_SITES_INFO.keys()),
                value=["LinkedIn"],
                label="Active Job Sites",
            )

            # Show site info
            site_info_parts = []
            for s, info in JOB_SITES_INFO.items():
                site_info_parts.append(f"**{s}** ({info['url']}) — {info['notes']}")
            gr.Markdown("**ℹ️ About each site:**\n\n" + "\n".join(f"- {p}" for p in site_info_parts))

            gr.Markdown("#### ✉️ Cover Letter Style")
            tone_in = gr.Radio(
                choices=[v[2] for v in COVER_TONES],
                value="Clean and formal",
                label="How should your cover letter sound?",
            )

            gr.Markdown("#### 🛠️ Do you have an AI agent?")
            gr.Markdown("*This is important! AI agents handle the smart parts of automation.*", visible=True)
            ai_mode_in = gr.Radio(
                choices=["🤖 Yes — I use QClaw, OpenClaw, or another AI",
                          "❌ No — just give me search links"],
                value="🤖 Yes — I use QClaw, OpenClaw, or another AI",
            )

            gr.Markdown("#### 🤖 Choose Your Automation Tool")
            tool_in = gr.Radio(
                choices=[v[2] for v in TOOL_CHOICES],
                value="Best option. The AI handles anti-bot, form filling, and errors automatically.",
                label="How will you run the script?",
            )

        # ════════════════════════════════════════════════════════════
        # TAB 4 — RESULTS
        # ════════════════════════════════════════════════════════════
        with gr.Tab("📤 Your Results"):
            gr.Markdown("### ✅ Your Generated Script & Materials")

            generate_btn = gr.Button("🚀 Generate My Script", variant="primary", size="lg")

            with gr.Row():
                with gr.Column(scale=2):
                    summary_out = gr.Markdown("*Fill in Steps 1-3, then click **Generate My Script***")
                with gr.Column(scale=1):
                    gr.Markdown("**Need help?**")
                    gr.Markdown("💬 Ask your AI agent: *'Run my job automation script'*")

            gr.Markdown("---")
            gr.Markdown("### 📄 Generated Python Script")
            script_out = gr.Code(label="automation_script.py", language="python", lines=25)

            gr.Markdown("---")
            gr.Markdown("### ✉️ Cover Letters (ready to copy-paste)")
            cl_out = gr.Markdown()

            gr.Markdown("---")
            gr.Markdown("### 🔗 Search URLs (open these in your browser)")
            urls_out = gr.Markdown()

            gr.Markdown("---")
            gr.Markdown("### ⚠️ Important — Read Before Running")
            disclaimer_out = gr.HTML()

    # ── EVENT HANDLERS ────────────────────────────────────────────────────────

    def on_generate(
        name, email, phone,
        role, preset,
        locations, work_type, seniority,
        sites, daily_cap, salary_local, salary_remote,
        exclusions, tone, ai_mode, tool,
        cv_up, cv_tx,
    ):
        tone_map  = {"Clean and formal": "Professional",
                      "Warm and approachable": "Friendly",
                      "Short and to the point": "Direct"}
        tone_val  = tone_map.get(tone, "Professional")
        ai_val    = "Yes" in ai_mode
        tool_map   = {v[2]: v[1] for v in TOOL_CHOICES}
        tool_val   = tool_map.get(tool, "agent-browser")
        locs_map   = {v[1]: k for k, v in WORK_TYPES}
        wt_val     = locs_map.get(work_type, work_type)
        sr_map     = {v[1]: v[0] for v in SENIORITY_OPTIONS}
        sr_val     = sr_map.get(seniority, seniority)

        summary, script, cl, urls, disc = generate_output(
            name, email, phone, role, preset,
            locations, wt_val, sr_val,
            sites, int(daily_cap), salary_local, salary_remote,
            exclusions, tone_val, ai_val, tool_val,
            cv_up, cv_tx,
        )
        return summary, script, cl, urls, disc

    generate_btn.click(
        fn=on_generate,
        inputs=[
            name_in, email_in, phone_in,
            role_in, preset_in,
            locs_in, wt_in, sr_in,
            sites_in, cap_in, sal_l, sal_r,
            excl_in, tone_in, ai_mode_in, tool_in,
            cv_up, cv_tx,
        ],
        outputs=[summary_out, script_out, cl_out, urls_out, disclaimer_out],
    )

    # ── SHARE / LAUNCH ────────────────────────────────────────────────────────
    gr.Markdown("""
    ---
    **💡 Tip:** Run this dashboard locally with:
    ```bash
    cd Job-Automation-Studio
    pip install gradio PyYAML
    python app.py
    ```
    Then open `http://localhost:7860` in your browser.
    """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
