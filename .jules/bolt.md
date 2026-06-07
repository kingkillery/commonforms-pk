## 2024-04-10 - Ultralytics YOLO predict verbose overhead
**Learning:** Ultralytics YOLO `model.predict()` has significant synchronous stdout blocking overhead when `verbose=True` (the default). In loops over multiple images, the terminal logging dramatically increases inference time (e.g., from ~5.5s to ~8.4s for 10 images in non-fast mode).
**Action:** Always pass `verbose=False` to `model.predict()` when running in production/batch environments to avoid unnecessary I/O overhead.
