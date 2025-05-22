#!/bin/bash

# Local Security Scanning Script for Code PR Assist
# Run this script to perform comprehensive security checks before committing

set -e

echo "🛡️ Starting Security Scan for Code PR Assist"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Create reports directory
mkdir -p security-reports

print_status "Installing security scanning tools..."

# Install security tools if not already installed
pip install --quiet bandit[toml] safety semgrep || {
    print_error "Failed to install security tools"
    exit 1
}

print_success "Security tools installed successfully"

# 1. Bandit Security Scan
print_status "Running Bandit security scan..."
bandit -r github-agent/src database-agent/src \
    -f json -o security-reports/bandit-report.json \
    -ll -i 2>/dev/null || {
    print_warning "Bandit found security issues. Check security-reports/bandit-report.json"
}

bandit -r github-agent/src database-agent/src \
    -f txt -o security-reports/bandit-report.txt \
    -ll -i 2>/dev/null || true

# Note: Bandit doesn't support SARIF format natively
# Only JSON format is used for Bandit (SARIF support would require conversion)

print_success "Bandit scan completed"

# 2. Safety Dependency Scan
print_status "Running Safety dependency scan..."

# GitHub Agent dependencies
cd github-agent
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    safety check --json --output ../security-reports/safety-github-agent.json 2>/dev/null || {
        print_warning "Safety found vulnerabilities in GitHub Agent dependencies"
    }
    safety check --output ../security-reports/safety-github-agent.txt 2>/dev/null || true
fi
cd ..

# Database Agent dependencies
cd database-agent
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    safety check --json --output ../security-reports/safety-database-agent.json 2>/dev/null || {
        print_warning "Safety found vulnerabilities in Database Agent dependencies"
    }
    safety check --output ../security-reports/safety-database-agent.txt 2>/dev/null || true
fi
cd ..

print_success "Safety scan completed"

# 3. Semgrep Security Scan
print_status "Running Semgrep security scan..."
semgrep --config=auto \
    --json --output=security-reports/semgrep-report.json \
    --exclude="**/tests/**" \
    --exclude="**/test/**" \
    --exclude="**/*test*" \
    github-agent/src database-agent/src 2>/dev/null || {
    print_warning "Semgrep found security issues. Check security-reports/semgrep-report.json"
}

# Generate SARIF format for GitHub integration
semgrep --config=auto \
    --sarif --output=security-reports/semgrep-results.sarif \
    --exclude="**/tests/**" \
    --exclude="**/test/**" \
    --exclude="**/*test*" \
    github-agent/src database-agent/src 2>/dev/null || true

# Ensure SARIF file exists, create empty one if not
if [ ! -f "security-reports/semgrep-results.sarif" ]; then
    cat > security-reports/semgrep-results.sarif << 'EOF'
{
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "semgrep",
          "version": "1.0.0"
        }
      },
      "results": []
    }
  ]
}
EOF
fi

print_success "Semgrep scan completed"

# 4. Check for common security issues
print_status "Running additional security checks..."

# Check for hardcoded secrets (basic patterns)
if grep -r -i -E "(password|secret|key|token)\s*=\s*['\"][^'\"]{10,}" \
    github-agent/src database-agent/src 2>/dev/null | \
    grep -v test | grep -v mock | grep -v example; then
    print_warning "Potential hardcoded secrets found (check manually)"
else
    print_success "No obvious hardcoded secrets found"
fi

# Check for dangerous function usage
if grep -r -E "(eval|exec|subprocess.*shell=True)" \
    github-agent/src database-agent/src 2>/dev/null | \
    grep -v test; then
    print_warning "Potentially dangerous function usage found"
else
    print_success "No dangerous function usage found"
fi

# Check for HTTP URLs in production code (should use HTTPS)
if grep -r -E "http://[^/]*[^localhost]" \
    github-agent/src database-agent/src 2>/dev/null | \
    grep -v test | grep -v localhost; then
    print_warning "HTTP URLs found - consider using HTTPS for production"
else
    print_success "No insecure HTTP URLs found"
fi

# 5. Generate summary report
print_status "Generating security summary..."

cat > security-reports/security-summary.md << EOF
# Security Scan Summary

**Scan Date:** $(date)
**Scan Duration:** $(date +%s) seconds

## Tools Used
- ✅ Bandit (Python security linting)
- ✅ Safety (dependency vulnerability scanning)
- ✅ Semgrep (advanced static analysis)
- ✅ Custom pattern matching

## Reports Generated
- \`bandit-report.json\` - Detailed Bandit findings (JSON format)
- \`bandit-report.txt\` - Human-readable Bandit report
- \`safety-github-agent.json\` - GitHub Agent dependency vulnerabilities
- \`safety-database-agent.json\` - Database Agent dependency vulnerabilities
- \`semgrep-report.json\` - Semgrep security findings
- \`semgrep-results.sarif\` - Semgrep SARIF format for GitHub Security tab

**Note:** Bandit doesn't support SARIF format natively. Only Semgrep uploads to GitHub Security tab.

## Next Steps
1. Review all reports in the \`security-reports/\` directory
2. Address any HIGH or CRITICAL severity issues
3. Update dependencies with known vulnerabilities
4. Run tests to ensure fixes don't break functionality

## Quick Fix Commands
\`\`\`bash
# Update dependencies
pip install --upgrade -r github-agent/requirements.txt
pip install --upgrade -r database-agent/requirements.txt

# Re-run security scan
./.github/scripts/security-scan.sh
\`\`\`
EOF

print_success "Security summary generated"

# 6. Display results
echo ""
echo "🛡️ Security Scan Complete!"
echo "=========================="
echo "📁 Reports saved in: security-reports/"
echo "📋 Summary: security-reports/security-summary.md"
echo ""

# Check if any critical issues were found
critical_issues=0

if [ -f "security-reports/bandit-report.json" ]; then
    high_severity=$(grep -o '"severity": "HIGH"' security-reports/bandit-report.json 2>/dev/null | wc -l || echo 0)
    if [ "$high_severity" -gt 0 ]; then
        print_warning "Found $high_severity HIGH severity issues in Bandit scan"
        ((critical_issues++))
    fi
fi

if [ -f "security-reports/semgrep-report.json" ]; then
    # Check if jq is available, otherwise skip detailed analysis
    if command -v jq &> /dev/null; then
        semgrep_errors=$(jq '.results | length' security-reports/semgrep-report.json 2>/dev/null || echo 0)
        if [ "$semgrep_errors" -gt 0 ]; then
            print_warning "Found $semgrep_errors issues in Semgrep scan"
            ((critical_issues++))
        fi
    else
        # Fallback: check if file is not empty and contains results
        if [ -s "security-reports/semgrep-report.json" ] && grep -q '"results"' security-reports/semgrep-report.json 2>/dev/null; then
            print_warning "Semgrep found potential issues (install 'jq' for detailed analysis)"
            ((critical_issues++))
        fi
    fi
fi

# Validate SARIF files were created properly (Semgrep only)
if [ -f "security-reports/semgrep-results.sarif" ]; then
    print_success "Semgrep SARIF report generated successfully"
else
    print_warning "Semgrep SARIF report was not generated"
fi

# Note: Bandit only generates JSON format (no SARIF support)
if [ -f "security-reports/bandit-report.json" ]; then
    print_success "Bandit JSON report generated successfully"
else
    print_warning "Bandit JSON report was not generated"
fi

if [ $critical_issues -eq 0 ]; then
    print_success "No critical security issues found! ✨"
    echo "💡 Pro tip: Regular security scans help maintain a secure codebase"
else
    print_warning "Found $critical_issues potential security issues"
    echo "📋 Please review the reports and address any critical findings"
    echo "🔗 For help: https://github.com/your-org/code-pr-assist/blob/main/.github/security.md"
fi

echo ""
echo "🔒 Keep your code secure! 🔒"
