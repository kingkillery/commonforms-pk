## 2025-04-18 - Remove Hardcoded Password
**Vulnerability:** Hardcoded password found in test file comments (`tests/inference_test.py`).
**Learning:** Even in test files, hardcoded credentials can expose sensitive information or be picked up by security scanners, creating false positives or actual risks if test passwords are reused.
**Prevention:** Use environment variables (e.g., `ENCRYPTED_PDF_PASSWORD`) for all credentials, even in tests, to maintain a clean and secure codebase.