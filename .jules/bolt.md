## 2024-04-17 - YOLO Stdout Blocking Overhead
**Learning:** Ultralytics YOLO models output verbose logs to stdout synchronously during `model.predict()`, which introduces significant blocking overhead when called inside loops or multiple times.
**Action:** Always pass `verbose=False` to `model.predict()` when doing batched or loop-based inference to bypass this synchronous blocking and improve performance.
