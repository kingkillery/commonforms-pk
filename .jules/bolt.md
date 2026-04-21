## 2026-04-18 - Ultralytics YOLO verbose Output Overhead
**Learning:** By default, Ultralytics YOLO models log predictions to stdout on every call. In a loop processing multiple pages, synchronous logging blocks the main thread, introducing significant unneeded performance overhead.
**Action:** Always pass `verbose=False` to `model.predict()` when running inference in loops or batch processes unless active debugging is needed.
