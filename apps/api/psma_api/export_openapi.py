from __future__ import annotations

import json
from pathlib import Path
import sys

from psma_api.main import app


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m psma_api.export_openapi <output_path>")
        return 2

    output_path = Path(sys.argv[1]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    schema = app.openapi()
    output_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote OpenAPI to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
