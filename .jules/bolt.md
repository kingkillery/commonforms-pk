## 2024-04-13 - Ultralytics YOLO Synchronous stdout Bottleneck
**Learning:** Ultralytics YOLO models by default print bounding box predictions and model details to stdout synchronously for every prediction call. Inside of loops or high-throughput batching, this blocks the main thread and introduces significant I/O latency, tanking performance.
**Action:** Always set `verbose=False` inside `.predict()` when using YOLO models in production or batch loops where logs are not explicitly needed.
