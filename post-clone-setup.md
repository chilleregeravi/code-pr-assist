# 🚀 Post-Clone Setup Guide

After cloning this repository, follow **ONE** of these setup methods:

## Method 1: One-Command Setup (Recommended)
```bash
./setup.sh
```
**What this does:**
- ✅ Sets up virtual environments for both agents
- ✅ Installs all dependencies
- ✅ **Automatically installs pre-commit hooks**
- ✅ Verifies everything works

## Method 2: Per-Agent Setup
```bash
# Setup GitHub Agent
cd github-agent
make setup

# Setup Database Agent
cd ../database-agent
make setup
```

## Method 3: DevContainer
If using VS Code with Dev Containers:
1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. **Pre-commit hooks are installed automatically**

## Method 4: Manual Setup
```bash
# Install pre-commit globally
pip install pre-commit

# Clone and navigate to repo
git clone <repo-url>
cd code-pr-assist

# Install pre-commit hooks
pre-commit install

# Setup individual agents
cd github-agent && make venv
cd ../database-agent && make venv
```

## ✅ Verification

After setup, verify pre-commit hooks are working:
```bash
# Make a small change to test
echo "# Test comment" >> README.md
git add README.md
git commit -m "test: Verify pre-commit hooks"
```

You should see output like:
```
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
GitHub Agent Tests.......................................................Passed
Database Agent Tests.....................................................Passed
check for merge conflicts................................................Passed
```

If hooks run automatically, **setup is complete!** 🎉

## 🆘 Troubleshooting

**Pre-commit hooks not running?**
```bash
# Check if hooks are installed
ls -la .git/hooks/
# Should show pre-commit file

# Reinstall hooks
pre-commit install
```

**Tests failing?**
```bash
# Run tests manually to see specific errors
cd github-agent && make test
cd ../database-agent && make test
```

**Environment issues?**
```bash
# Clean and rebuild environment
make clean
make setup
```
