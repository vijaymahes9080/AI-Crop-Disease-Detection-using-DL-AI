#!/bin/bash
# run_tests.sh
echo "[*] Initializing AgroVision Test Suite..."

# 1. Run unit, integration, and security tests with pytest
pytest tests/ \
    --cov=app \
    --cov-config=.coveragerc \
    --cov-report=html:reports/htmlcov \
    --cov-report=term-missing \
    --junitxml=reports/junit-report.xml

# 2. Check coverage results
if [ $? -eq 0 ]; then
    echo "[+] PyTest Suite completed successfully. Reports saved to 'reports/'."
else
    echo "[!] PyTest Suite encountered failures."
    exit 1
fi

# 3. Code Style Audit
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
