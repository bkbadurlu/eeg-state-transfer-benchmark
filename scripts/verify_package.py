"""Standard-library integrity and syntax verification; does not import fits."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    errors = []
    for name, expected in manifest.items():
        p = ROOT / name
        if not p.is_file():
            errors.append('missing: ' + name)
        elif hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            errors.append('hash mismatch: ' + name)
        if p.is_file() and p.suffix == '.py':
            try:
                ast.parse(p.read_text(encoding='utf-8-sig'), filename=name)
            except SyntaxError as exc:
                errors.append(str(exc))
    if errors:
        raise SystemExit('\n'.join(errors))
    print(json.dumps({'status': 'PASS_SHA256_AND_SYNTAX', 'files': len(manifest)}))


if __name__ == '__main__':
    main()
