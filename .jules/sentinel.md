## 2025-04-08 - Remove Hardcoded Password in Test Comments
**Vulnerability:** Hardcoded password for an encrypted PDF found in test comments (`tests/inference_test.py`).
**Learning:** Developers often leave credentials in comments for convenience in test files, underestimating the risk of leaking sensitive information or personal passwords.
**Prevention:** Avoid committing sensitive credentials or personal passwords in any code artifacts, including comments and tests. Use environment variables or secure vault integrations instead if testing with protected data is required.