"""Run all six reconstructed notebook cells. Python 3.9+."""
from pathlib import Path
import os
import sys

if not __debug__:
    raise SystemExit("Run without -O: this lab requires assertions for verification.")

code_dir = Path(__file__).resolve().parent
output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/latest").resolve()
output_dir.mkdir(parents=True, exist_ok=True)
os.chdir(output_dir)
state = {"__name__": "__main__"}
try:
    for number in range(1, 7):
        path = code_dir / f"cell-{number:02d}.py"
        exec(compile(path.read_text(), str(path), "exec"), state)
finally:
    if "server" in state:
        state["server"].shutdown()
        state["server"].server_close()
print(f"Outputs saved to {output_dir}")
