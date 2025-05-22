# 🤖 Dependabot Auto-Merge Setup

This repository includes an automated workflow that safely merges Dependabot pull requests for patch and minor updates after ensuring all CI checks pass.

## 🚀 Features

### **Automatic Merging**
- ✅ **Patch updates** (1.2.3 → 1.2.4) - Bug fixes, backwards compatible
- ✅ **Minor updates** (1.2.3 → 1.3.0) - New features, backwards compatible
- ✅ **Security updates** - Critical security patches
- ❌ **Major updates** (1.2.3 → 2.0.0) - Requires manual review

### **Safety Checks**
- 🧪 **All CI tests must pass** before auto-merge
- 📝 **Automatic approval** for safe updates
- 🏷️ **Smart labeling** based on update type
- 📋 **Detailed comments** for major updates requiring review

### **Workflow Jobs**
1. **`dependabot`** - Handles patch/minor updates
2. **`security-updates`** - Handles security-related updates
3. **`notification`** - Adds labels and comments

## 🔧 Setup Instructions

### 1. **Create Required Labels**
Run this once to set up GitHub labels:
```bash
# Install GitHub CLI if not already installed
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Login to GitHub
gh auth login

# Create labels
.github/scripts/setup-labels.sh
```

**Or create labels manually in GitHub:**
- `auto-merge` (🟢 Green) - PRs that can be automatically merged
- `manual-review` (🔴 Red) - PRs requiring manual review
- `patch-update` (🟡 Yellow) - Patch version updates
- `minor-update` (🔵 Blue) - Minor version updates
- `major-update` (🔴 Dark Red) - Major version updates
- `dependencies` (🔵 GitHub Blue) - Dependency updates

### 2. **Configure Repository Settings**
Ensure these settings are enabled in your repository:

**Settings → General → Pull Requests:**
- ✅ Allow auto-merge
- ✅ Automatically delete head branches

**Settings → Branches → Branch protection rules for `main`:**
- ✅ Require status checks to pass before merging
- ✅ Require up-to-date branches before merging
- ✅ Include administrators (optional but recommended)

## 📋 How It Works

### **Patch/Minor Updates (Auto-merged)**
1. Dependabot creates PR
2. Workflow detects update type
3. Auto-approves the PR
4. Waits for all CI checks to pass
5. Auto-merges with squash merge
6. Adds `auto-merge` + `patch-update`/`minor-update` labels

### **Major Updates (Manual review)**
1. Dependabot creates PR
2. Workflow detects major update
3. Adds detailed comment with review checklist
4. Adds `manual-review` + `major-update` labels
5. **Waits for human approval** - no auto-merge

### **Security Updates (Auto-merged)**
1. Dependabot creates security PR
2. Workflow detects security alert
3. Auto-approves immediately
4. Waits for CI checks
5. Auto-merges after successful tests

## 🔍 Example Workflows

### ✅ **Successful Auto-merge (Patch)**
```
📝 Dependabot: Bump requests from 2.28.1 to 2.28.2
🤖 Auto-approve: ✅ Approved
🧪 CI Checks: ✅ All passed
🔀 Auto-merge: ✅ Merged
🏷️ Labels: auto-merge, patch-update, dependencies
```

### ⚠️ **Manual Review Required (Major)**
```
📝 Dependabot: Bump fastapi from 0.95.0 to 1.0.0
🚨 Comment: Major update detected - manual review required
🏷️ Labels: manual-review, major-update, dependencies
👤 Human: Review changelog, test locally, then merge
```

### 🛡️ **Security Update (Auto-merged)**
```
📝 Dependabot: Bump cryptography from 3.4.8 to 41.0.4 (security)
🛡️ Security: Critical vulnerability fix
🤖 Auto-approve: ✅ Approved immediately
🧪 CI Checks: ✅ All passed
🔀 Auto-merge: ✅ Merged
```

## 🛡️ Security Considerations

### **Safe by Design**
- Only auto-merges **after CI passes**
- Only handles **patch/minor/security** updates
- **Major updates always require human review**
- Uses **squash merge** to maintain clean history

### **Fail-Safe Behavior**
- If any CI check fails → **No auto-merge**
- If update type is major → **No auto-merge**
- If workflow fails → **Falls back to manual review**

## 🔧 Customization

### **Modify Update Types**
Edit `.github/workflows/auto-merge.yml`:
```yaml
# To allow major updates (not recommended):
if: ${{ steps.metadata.outputs.update-type == 'version-update:semver-major' }}

# To exclude minor updates:
if: ${{ steps.metadata.outputs.update-type == 'version-update:semver-patch' }}
```

### **Change Merge Strategy**
```yaml
# Use merge commit instead of squash:
gh pr merge --auto --merge "$PR_URL"

# Use rebase:
gh pr merge --auto --rebase "$PR_URL"
```

### **Adjust Wait Times**
```yaml
# Increase timeout for slow CI:
wait-interval: 30  # Check every 30 seconds instead of 15
```

## 📊 Monitoring

### **View Auto-merge Activity**
```bash
# List recent auto-merged PRs:
gh pr list --state merged --label "auto-merge" --limit 10

# Check Dependabot PRs:
gh pr list --author "dependabot[bot]" --state all
```

### **Workflow Logs**
- Go to **Actions** tab in GitHub
- Click on **Auto-merge Dependabot PRs** workflow
- Review logs for any issues

## 🚨 Troubleshooting

### **Auto-merge Not Working**
1. ✅ Check branch protection rules are configured
2. ✅ Verify "Allow auto-merge" is enabled
3. ✅ Ensure CI checks are passing
4. ✅ Check workflow permissions in `.github/workflows/auto-merge.yml`

### **CI Checks Failing**
1. Review test logs in CI workflow
2. Check if dependency update broke tests
3. Fix tests and push to PR branch
4. Auto-merge will trigger after CI passes

### **Labels Missing**
Run the setup script to create missing labels:
```bash
.github/scripts/setup-labels.sh
```

## 📈 Benefits

- ⚡ **Faster dependency updates** - No manual intervention for safe updates
- 🛡️ **Enhanced security** - Security patches applied immediately
- 🧪 **Maintained quality** - All tests must pass before merge
- 📋 **Clear audit trail** - Proper labeling and comments
- 🔄 **Reduced maintenance** - Less manual PR review overhead

---

💡 **Pro Tip**: Monitor the auto-merge activity weekly to ensure dependencies stay current and secure!

## 🔗 Related Files

- [`.github/workflows/auto-merge.yml`](.github/workflows/auto-merge.yml) - Main auto-merge workflow
- [`.github/dependabot.yml`](.github/dependabot.yml) - Dependabot configuration
- [`.github/scripts/setup-labels.sh`](.github/scripts/setup-labels.sh) - Label setup script
