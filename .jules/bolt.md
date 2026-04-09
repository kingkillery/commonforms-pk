## 2024-05-24 - Ultralytics YOLO verbose Output Blocking
**Learning:** For performance optimization with Ultralytics YOLO models, `model.predict()` can have significant synchronous stdout blocking overhead during loops.
**Action:** Pass `verbose=False` to `model.predict()` to avoid synchronous stdout blocking overhead when processing multiple items or looping.
