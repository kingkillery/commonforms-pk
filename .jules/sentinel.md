## 2025-04-17 - Hardcoded Secrets in Test Files
**Vulnerability:** Hardcoded password found in test file comment (`tests/inference_test.py`).
**Learning:** Hardcoded credentials in any codebase artifacts, including test files and comments, are security vulnerabilities and can lead to accidental leaks or scanner warnings. Developers sometimes leave passwords in comments as reminders.
**Prevention:** Never hardcode passwords or credentials anywhere. Always use environment variables for sensitive data, even in tests or comments.
