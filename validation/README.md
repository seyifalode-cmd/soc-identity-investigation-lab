# Validation

Run from the repository root with Python 3.9+:

```bash
python3 validation/check_project.py
```

The standard-library suite tests the actual detector loaded from cell 1. It covers shuffled event arrival, user/application separation, a one-second window overrun, repeated success delivery, exact evidence IDs, multiple successes, and the documented last-record-wins event-ID limitation.

Repository checks validate the six-cell notebook against source files, original PDF hashes, six/three CSV fixture counts, and local Markdown file links. The integration check runs all six cells in a temporary output directory, checks the single exported alert and expected response audit sequence, and confirms the runner refuses `-O`. Subprocesses have timeouts so a hung run fails validation.

The original ten detector assertions and HTTP checks remain in the executable lab. Additional unit tests do not claim more attack coverage, a measured false-positive rate, or live Azure/Jira validation. The saved [regression report](../evidence/local-validation/regression.txt) is a local execution result.
