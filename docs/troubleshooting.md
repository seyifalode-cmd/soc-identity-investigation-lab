# Troubleshooting and cleanup

| Symptom | Likely cause | Action |
|---|---|---|
| Python command unavailable | Python is not installed or uses a different command | Use your Python 3.9+ interpreter; check its version before running |
| Runner refuses `-O` | Optimized mode removes assertions | Run `python3 code/run_lab.py` without optimization |
| Notebook `NameError` | Cells ran out of order or the runtime restarted | Restart and run cells 1–6 in order |
| Notebook connection refused | Server was stopped or cell 4 did not run | Run cell 4 to establish a fresh baseline, then cells 5 and 6 |
| Azure table not found | Wrong database or missing schema | Select the intended training database and check table names |
| Azure count greater than six | Repeated ingestion appended duplicates | Use a new empty lab database for a clean replay; do not delete unrelated data |
| No events in query interval | Relative time filter excludes the fixed fixture | Use the explicit 23 September 2026 UTC interval |
| Azure management command error | Multiple blocks run together | Run each numbered `.create`/`.ingest` block separately |
| Jira relationship absent | Link was not saved or an accidental subtask was created | Open the work item and verify the saved relates-to relationship |
| Colab JSON exports disappeared | Temporary runtime was discarded | Re-run the lab and save both files before disconnecting |
| Regression suite reports a hash mismatch | A source PDF differs from its recorded original | Inspect the change; do not overwrite the manifest merely to make the check pass |
| A response assertion fails | Actual request result differs from the expected control effect | Save the traceback and audit; investigate the failing path before marking completion |

## Output locations

Local runs write to `runs/latest/` by default; an explicit path creates a separate run directory. Reusing a path overwrites that run's two JSON output files. The repository's saved evidence lives in `evidence/local-validation/`; choose a new run directory when preserving additional evidence.

The regression suite uses a temporary directory and checks the generated artifacts before removing it. Its captured console results are available during the run; redirect them if you need a durable transcript.

## Cleanup

The local runner closes the training server in a `finally` block. In a notebook, cell 6 closes it; if a cell fails before that point, restart the kernel/runtime to stop the server and clear state. Export the evidence first. Cloud workspace cleanup is separate and is not performed by any repository script.
