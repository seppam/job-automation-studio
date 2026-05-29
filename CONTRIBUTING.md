# Contributing to Job Automation Studio

## How to Contribute

1. **Fork the repo** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/job-automation-studio.git
   cd job-automation-studio
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** — add job sites, fix bugs, improve docs
5. **Test** your changes by running the dashboard:
   ```bash
   pip install gradio PyYAML
   python app.py
   ```
6. **Commit** your changes:
   ```bash
   git commit -m "Add: new feature or fix description"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. Open a **Pull Request** on GitHub

---

## What to Contribute

### 🐛 Bug Fixes
Found a bug? Fix it and open a PR. Please describe the bug in the PR description.

### 🌐 New Job Sites
Add a new site to `SITES/directory.yml`. Follow the existing format:
```yaml
my_new_site:
  display_name: "My New Site"
  url: "https://example.com"
  search_url_pattern: "https://example.com/jobs?q={role}&l={location}"
  easy_apply: true  # or false
  notes: "Short description"
```

### 📖 Documentation
Typos, better explanations, translations — all welcome.

### ⚡ New Features
Have an idea? Open an issue first to discuss it before building.

---

## Code Style

- Use Python 3.10+
- 4-space indentation (no tabs)
- Docstrings for functions
- Keep functions small and focused

---

## Reporting Issues

Open an issue on GitHub with:
1. What you expected to happen
2. What actually happened
3. Steps to reproduce
4. Your OS and Python version
