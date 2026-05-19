## 2025-04-05 - Memory blowup with batch inference in Ultralytics YOLO
**Learning:** By default, calling `model.predict(list_of_images)` on a YOLO model stores all prediction `Result` objects (including original image arrays and tensors) in a list in memory. For a large batch (like pages in a PDF), this causes massive memory spikes.
**Action:** Always use `stream=True` when passing a list of inputs to `model.predict()` in Ultralytics to return a generator and reduce peak memory usage from O(N) to O(1) with respect to output tensors.
