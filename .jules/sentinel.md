## 2024-04-11 - Hardcoded Test Passwords
**Vulnerability:** Hardcoded password found in test comment (`tests/inference_test.py`).
**Learning:** Even if it's just a test asset password, hardcoded credentials trigger secret scanners and violate security standards.
**Prevention:** Use environment variables for all credentials, even for test fixtures or in comments.
