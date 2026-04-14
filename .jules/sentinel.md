## 2024-05-18 - Exposed Password in Test Comments
**Vulnerability:** Hardcoded password "kanbanery" found in tests/inference_test.py comments.
**Learning:** Hardcoded secrets in comments are a security risk and should be removed.
**Prevention:** Use environment variables for test passwords.
