## 2024-05-18 - YOLO Stdout Blocking Overhead
**Learning:** Ultralytics YOLO models by default output synchronous progress logs to stdout during `.predict()`. This synchronous I/O blocking can significantly slow down prediction loops in production applications where the logs are not useful.
**Action:** Always pass `verbose=False` to `model.predict()` when using YOLO models in automated processing pipelines to avoid unnecessary I/O blocking.
