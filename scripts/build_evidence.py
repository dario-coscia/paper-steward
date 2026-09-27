"""Record or inspect build evidence; inspection never writes files."""
from pathlib import Path
import hashlib
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]

def hashes():
    paths = [p for p in (ROOT / "paper").rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".csv", ".pdf", ".json"}]
    paths += [ROOT / "scripts/build.sh"]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def evidence(out):
    pdf, log = out / "main.pdf", out / "main.log"
    if not pdf.is_file() or not log.is_file(): raise ValueError("Missing build PDF/log; run sh scripts/build.sh")
    text = log.read_text(errors="replace")
    if "Output written on" not in text or re.search(r"Warning:|Overfull|^!", text, re.M):
        raise ValueError("Build log lacks success or contains warnings/errors; inspect build/main.log")
    return {"sources": hashes(), "pdf": hashlib.sha256(pdf.read_bytes()).hexdigest(), "log": hashlib.sha256(log.read_bytes()).hexdigest()}

def main():
    mode = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "build"
    receipt = out / "evidence.json"
    try:
        current = evidence(out)
        if mode == "record": receipt.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        elif mode == "check":
            if json.loads(receipt.read_text()) != current: raise ValueError("Build evidence is stale; run sh scripts/build.sh")
        else: raise ValueError("Expected record or check")
    except (ValueError, OSError) as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
