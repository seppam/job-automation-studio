# 🔧 Tool Setup Guides

Detailed installation instructions for each automation tool.

---

## OpenClaw / QClaw Setup

### What is it?
OpenClaw is a self-hosted AI agent that runs on your machine. It has built-in browser control, so it can run your automation script like a human would.

### Install
```bash
# Requires Node.js (v18+) and npm
npm install -g openclaw

# Or for QClaw:
# (follow the QClaw installation guide for your platform)

# Start the gateway
openclaw gateway start
```

### Using it
```bash
# Tell your AI to run the script:
"Run my job automation script at /path/to/script.py"
```

The AI will automatically handle:
- Opening the browser
- Navigating to job sites
- Logging in
- Filling forms
- Handling anti-bot blocks
- Writing personalised cover letters

### Docs
→ https://docs.openclaw.ai

---

## Playwright Setup

### Install
```bash
# Requires Python 3.8+
pip install playwright
playwright install chromium
```

### Test it works
```python
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

### Run a script
```bash
python your_script.py
```

### Common issues

**"chromium not installed"**
```bash
playwright install chromium
```

**"Permission denied" (Mac/Linux)**
```bash
sudo pip install playwright
sudo playwright install chromium
```

---

## Selenium Setup

### Install
```bash
pip install selenium
```

### Download ChromeDriver
1. Check your Chrome version: `chrome://settings/help`
2. Download matching ChromeDriver: https://chromedriver.chromium.org/downloads
3. Add to system PATH, or put it in your project folder

### Verify
```bash
python -c "from selenium import webdriver; print('Selenium OK')"
```

### Run
```bash
python your_script.py
```

---

## VPN (Recommended for Anti-Bot)

If you're getting rate-limited on LinkedIn, use a VPN.

**Recommended VPNs:**
- **ProtonVPN** (free tier available)
- **Windscribe** (free 10GB/month)
- **NordVPN**

**Tip:** Switch to a residential IP if possible — datacenter IPs are more likely to be flagged by LinkedIn.

---

## Keeping Things Running Smoothly

1. **Don't run more than 50 applications/day** on LinkedIn — you'll get rate-limited
2. **Use off-peak hours** (early morning or late night local time) — less anti-bot detection
3. **Rotate VPNs** if using one — same IP for weeks looks suspicious
4. **Re-generate your script** every 2 weeks — job sites update their UIs often
5. **Keep your CV updated** — the script pulls from your latest CV
