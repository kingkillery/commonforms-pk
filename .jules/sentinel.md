## 2025-02-28 - Removed hardcoded password from test file comment
**Vulnerability:** A hardcoded password ("kanbanery") was found in a comment within `tests/inference_test.py`.
**Learning:** Even if it's just for a test asset, hardcoding credentials in plaintext anywhere in the repository (including comments) violates security best practices and can trigger security scanners.
**Prevention:** Always rely on environment variables (e.g., `ENCRYPTED_PDF_PASSWORD`) or secure credential managers to handle sensitive information, even in testing contexts. Never hardcode plaintext secrets.
