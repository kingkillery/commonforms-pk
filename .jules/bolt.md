## 2024-05-18 - Ultralytics YOLO verbose synchronous I/O
**Learning:** Ultralytics YOLO models print detailed inference logs (timing, image size, detected objects) to stdout by default for every single prediction. Inside list comprehensions or inference loops, this synchronous stdout blocking creates noticeable overhead and slows down the loop unnecessarily.
**Action:** Always add `verbose=False` to `model.predict()` when calling YOLO models in loops or production environments where stdout logging is not needed to prevent I/O blocking overhead.
