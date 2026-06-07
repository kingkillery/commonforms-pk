## 2024-04-12 - Disable synchronous stdout logging in Ultralytics YOLO inference
**Learning:** Ultralytics YOLO models write detailed inference stats to stdout by default on every prediction. Synchronous logging to stdout creates blocking I/O overhead that accumulates, particularly when processing sequences of inputs (like document pages) inside loops.
**Action:** Always set `verbose=False` in `model.predict()` (and similar model inference calls) within loop bodies or production code paths to prevent unnecessary I/O blocking overhead, improving throughput.
