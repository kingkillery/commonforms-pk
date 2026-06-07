## 2024-05-15 - Ultralytics YOLO verbose=False
**Learning:** By default, Ultralytics YOLO models log prediction details to stdout. In batch jobs or loops, this synchronous print blocking can cause significant performance overhead (tested 77s down to ~38s on batch of 20 images).
**Action:** Always add `verbose=False` to `model.predict()` in tight loops or large batch inferencing to avoid synchronous stdout blocking overhead.
