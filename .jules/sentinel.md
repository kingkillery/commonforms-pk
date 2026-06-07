## 2025-10-18 - Hardcoded Password in Test File
**Vulnerability:** A hardcoded password ("kanbanery") was found in a comment within `tests/inference_test.py`.
**Learning:** Developers often leave hardcoded credentials in tests or test comments for convenience or as reminders, overlooking that these are still committed to version control and pose a security risk if the repository becomes public or is compromised.
**Prevention:** Never hardcode passwords or credentials in any codebase artifacts, including test files and comments. Use environment variables (e.g., `os.environ.get('ENCRYPTED_PDF_PASSWORD')`) to manage test credentials securely.
