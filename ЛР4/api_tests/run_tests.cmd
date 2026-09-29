@echo off
rem Run API tests (LR4)

echo === Running API tests ===

if not exist reports mkdir reports

set PYTHONPATH=%PYTHONPATH%;.

echo 1. Full test run...
py -m pytest tests/ -v

echo 2. Smoke tests only...
py -m pytest tests/ -m smoke -v

echo === Done ===
echo HTML report: reports/report.html
echo JUnit report: reports/junit.xml
