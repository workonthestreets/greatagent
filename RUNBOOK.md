# Reality Test runbook (16:30–17:00 BST)

1. **16:30: code freeze.** Do not change any code after this point. Note the commit hash (`git rev-parse HEAD`) for the submission form. `python3 tools_fingerprint.py` prints the code fingerprint that every run records in `ANSWERS/run_manifest.json`.
2. **Get the cases.** Download or clone the released cases into a folder, for example `~/Desktop/RealityTest/`.
3. **Run everything with one command:**
   ```bash
   ./reality.sh "/path/to/RealityTest"            # or: python3 run.py <folder> --out ANSWERS --workers 12 --resume
   ```
   - A case takes about 30–60 s, and cases run in parallel.
   - The run can be resumed: running it again skips cases that already have a result and retries any that failed.
   - A case that still fails gets an honest `SYSTEM FAILURE` answer, with nothing sent and a human handover.
4. **Check without editing.**
   - Open `ANSWERS/SUMMARY.md` and `ANSWERS/index.html`.
   - Never hand-edit an `ANSWER.md`. The rules forbid replacing agent outputs.
   - If a case crashed, re-run it with `--resume`. That is still the system's output.
5. **Commit and push `ANSWERS/` before 17:00:**
   ```bash
   git add ANSWERS && git commit -m "Reality Test results" && git push
   ```
6. **Fill in the form.** Give the repo URL, the 16:30 commit hash, `ANSWERS/` as the results path, `demo/demo.mp4` as the video path, and the LinkedIn and X post URLs.

Folder layouts the runner accepts:
- a single case folder
- a folder of case folders
- a folder of track folders
- a flat folder of `.md`/`.txt`/`.json` case files

Answer folders use the case number with leading zeros removed (`007` → `ANSWERS/7`).
