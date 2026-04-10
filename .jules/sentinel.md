## 2024-04-10 - Hardcoded password in tests
**Vulnerability:** A hardcoded password ("kanbanery") was found in a comment in `tests/inference_test.py`.
**Learning:** Hardcoded credentials even in test comments or disabled code are security risks and violate security conventions.
**Prevention:** Never hardcode passwords in test files or comments. Use environment variables (e.g., TEST_PDF_PASSWORD) instead.
