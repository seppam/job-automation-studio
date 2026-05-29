# 📖 Detailed Setup Guide

> 💡 **Prefer pictures?** Download the **[Visual SOP Guide (PDF)](Job-Automation-Studio-SOP.pdf)** for step-by-step screenshots.

Follow this guide step by step if you're new to Python or automation tools.

---

## Prerequisite Check

Before starting, check what you already have:

### On Mac / Linux
Open Terminal and run:
```bash
python3 --version
```
You should see something like `Python 3.10.0` or higher.

### On Windows
Open Command Prompt and run:
```bash
python --version
```

---

## Step 1 — Install Python

**Download:** https://www.python.org/downloads/

Run the installer and **check "Add Python to PATH"** (Windows).

On Mac, you can also use Homebrew:
```bash
brew install python3
```

---

## Step 2 — Download This Project

**Option A — Download ZIP (easiest for beginners)**
1. Go to the GitHub repo
2. Click the green **Code** button
3. Click **Download ZIP**
4. Extract the ZIP to your Documents folder

**Option B — Clone with Git**
```bash
git clone https://github.com/YOUR_USERNAME/job-automation-studio.git
cd job-automation-studio
```

---

## Step 3 — Install Dependencies

Open your terminal/command prompt and run:

```bash
pip install gradio PyYAML
```

On some systems, you may need:
```bash
pip3 install gradio PyYAML
```

If you get a permission error:
```bash
pip install --user gradio PyYAML
```

---

## Step 4 — Run the Dashboard

```bash
python app.py
```
or
```bash
python3 app.py
```

You should see something like:
```
Running on local URL: http://127.0.0.1:7860
```

Open your browser and go to: **http://localhost:7860**

---

## Step 5 — Using the Dashboard

### For Non-Technical Users (AI Mode)

1. **Step 1:** Fill in your name, email, and upload your CV
2. **Step 2:** Pick your target job, locations, and salary
3. **Step 3:** Choose job sites
4. Click **"Generate My Script"**
5. **Download the generated .py file**
6. Give it to your AI agent with the instruction:
   > *"Run my job automation script at /path/to/downloaded/script.py"*

Done! Your AI agent will handle the rest.

---

## Step 6 — Setting Up AI Agent Integration

### QClaw / OpenClaw
If you have QClaw or OpenClaw installed, just tell it:
> *"Run my job automation script from /path/to/script.py"*

The AI will automatically use its built-in browser control to run the script.

### Claude (claude.ai)
Upload the script and say:
> *"Run this Python script and automate my job applications on LinkedIn"*

### Other AI Agents
Most AI coding agents (Cursor, GitHub Copilot, etc.) can also run the script
if they have access to a terminal or browser.

---

## Troubleshooting

### "pip: command not found"
Try:
```bash
python -m pip install gradio PyYAML
```

### "python: command not found"
On Windows, use `python3` instead of `python`.

On Mac, install Python from python.org or use Homebrew.

### "Port 7860 already in use"
Another app is using that port. Change the port:
```bash
python app.py --server-port 7861
```

### Gradio interface looks broken
Use Chrome or Edge browser. Safari sometimes has issues with Gradio.

### "No module named 'gradio'"
Re-run:
```bash
pip install gradio
```

### Still stuck?
→ Open an issue on GitHub
→ Or ask your AI agent: *"My Python/Gradio setup isn't working — help me debug"*

---

## Keeping Your Script Up to Date

Job sites change their UIs frequently. Best practice:
1. Re-run the dashboard every 1-2 weeks
2. Re-generate your script
3. If a site stops working, check if they updated their layout
4. Download a fresh script and replace the old one

---

## Uninstalling

```bash
pip uninstall gradio PyYAML
```
Delete the project folder. That's it!
