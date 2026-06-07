## 2024-04-07 - Ultralytics YOLO Predict I/O Bottleneck
**Learning:** By default, Ultralytics `YOLO.predict()` logs inference metrics (image shapes, timing) to stdout for every image. When processing multiple images (e.g., iterating through pages in ONNX fast mode or batching in PyTorch mode), this synchronous I/O blocks the main thread and introduces significant overhead (~8% execution time on short documents, worse on long ones).
**Action:** Always pass `verbose=False` to `model.predict()` in production loops or batched inference to disable unnecessary console logging.
