## 2024-06-25 - YOLO Synchronous stdout blocking overhead
**Learning:** Ultralytics YOLO models write synchronously to stdout during predictions. In a loop, this causes synchronous stdout blocking overhead which significantly impacts performance.
**Action:** Always pass `verbose=False` to `model.predict()` when calling YOLO models in a loop or production environment to avoid this overhead.
