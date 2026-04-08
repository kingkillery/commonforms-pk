1. **Optimize YOLO `model.predict` in `commonforms/inference.py`**
   - Pass `verbose=False` to `self.model.predict()` in both the fast-mode loop and the batch-mode call. This prevents synchronous stdout blocking overhead when processing many pages, making the inference step measurably faster.
   - Add a comment explaining the optimization.
2. **Add a journal entry in `.jules/bolt.md`**
   - Create/update `.jules/bolt.md` recording the performance bottleneck caused by Ultralytics YOLO synchronous stdout blocking overhead.
3. **Pre-commit checks**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
4. **Submit**
   - Create a PR with title `⚡ Bolt: [performance improvement]` and the required description format.
