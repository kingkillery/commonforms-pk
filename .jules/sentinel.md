## 2025-04-05 - Add image size bounds checking
**Vulnerability:** Missing upper bound on `image_size` input.
**Learning:** A missing upper limit on image size input for the CLI tool opens up a Denial of Service (DoS) vulnerability. A user providing a very large image size value could exhaust memory and cause Out-Of-Memory (OOM) errors during inference.
**Prevention:** Always set an upper bound for any configuration parameter that allocates memory (like image size bounds) to prevent resource exhaustion attacks.