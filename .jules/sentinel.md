## 2025-04-09 - Hardcoded Password in Test Comments
**Vulnerability:** A hardcoded password ("kanbanery") was found in a comment within `tests/inference_test.py` used to decrypt a test PDF.
**Learning:** Even though it was "just a test file" and a comment, any hardcoded secret is a potential security risk and violates the project's security convention. It can easily be leaked or trip automated security scanners, causing unnecessary noise.
**Prevention:** Never hardcode credentials, even in comments or test files. Use environment variables (e.g., `PDF_TEST_PASSWORD`) to document or pass secrets securely.
