## 2024-05-24 - Ultralytics YOLO Synchronous Logging Overhead
**Learning:** Calling `model.predict()` in Ultralytics YOLO with the default settings causes synchronous stdout writes that can introduce blocking overhead, especially when called inside loops or handling multiple items.
**Action:** Always explicitly pass `verbose=False` to `model.predict()` unless debugging output is actively required. This prevents unnecessary I/O overhead.
