## 2025-04-12 - Critical: Avoid Hardcoded Credentials in Test Comments

**Vulnerability:** A hardcoded password ("kanbanery") for an encrypted PDF file was found in a comment within `tests/inference_test.py`.
**Learning:** Comments in test files can inadvertently leak sensitive information, such as passwords used for test resources. Hardcoded secrets, even when intended purely for internal or test use, can pose a risk if the repository is ever compromised or exposed.
**Prevention:** Never include passwords or other sensitive secrets in the codebase, including in code comments or test scripts. If passwords are required for testing, they should be managed via environment variables or a secure secret manager, and test resources should ideally use widely known, non-sensitive credentials (e.g., "password123") if they must be embedded.
