"""Compare two YOLO training runs by metrics and confusion matrices.

Usage:
    python compare_yolo_runs.py \
        --run-a runs/pothole_detection_old \
        --run-b runs/pothole_detection \
        --label-a YOLOv8n \
        --label-b YOLOv8s

The script reads each run's `results.csv`, prints the final-epoch metrics,
and combines `confusion_matrix.png` / `confusion_matrix_normalized.png`
into a side-by-side comparison image.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont


METRIC_COLUMNS = [
    "metrics/precision(B)",
    "metrics/recall(B)",
    "metrics/mAP50(B)",
    "metrics/mAP50-95(B)",
]


def read_last_row(csv_path: Path) -> Optional[Dict[str, str]]:
    if not csv_path.exists():
        return None
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return rows[-1] if rows else None


def format_metric(value: Optional[str]) -> str:
    if value is None or value == "":
        return "n/a"
    try:
        return f"{float(value):.4f}"
    except ValueError:
        return str(value)


def collect_run_summary(run_dir: Path) -> Dict[str, str]:
    row = read_last_row(run_dir / "results.csv")
    summary = {
        "run_dir": str(run_dir),
        "epoch": "n/a",
        "precision": "n/a",
        "recall": "n/a",
        "map50": "n/a",
        "map50_95": "n/a",
    }
    if row:
        summary["epoch"] = str(row.get("epoch", "n/a"))
        summary["precision"] = format_metric(row.get("metrics/precision(B)"))
        summary["recall"] = format_metric(row.get("metrics/recall(B)"))
        summary["map50"] = format_metric(row.get("metrics/mAP50(B)"))
        summary["map50_95"] = format_metric(row.get("metrics/mAP50-95(B)"))
    return summary


def find_confusion_image(run_dir: Path) -> Optional[Path]:
    candidates = [
        run_dir / "confusion_matrix_normalized.png",
        run_dir / "confusion_matrix.png",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_image_with_label(image_path: Path, label: str) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    canvas = Image.new("RGB", (img.width, img.height + 64), "white")
    canvas.paste(img, (0, 64))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((16, 18), label, fill="black", font=font)
    draw.text((16, 34), image_path.name, fill="gray", font=font)
    return canvas


def build_contact_sheet(left: Image.Image, right: Image.Image) -> Image.Image:
    gap = 24
    height = max(left.height, right.height)
    sheet = Image.new("RGB", (left.width + right.width + gap, height), (245, 245, 245))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + gap, 0))
    return sheet


def print_summary(label: str, summary: Dict[str, str], confusion_path: Optional[Path]) -> None:
    print(f"\n[{label}]")
    print(f"  Run dir   : {summary['run_dir']}")
    print(f"  Last epoch : {summary['epoch']}")
    print(f"  Precision  : {summary['precision']}")
    print(f"  Recall     : {summary['recall']}")
    print(f"  mAP50      : {summary['map50']}")
    print(f"  mAP50-95   : {summary['map50_95']}")
    print(f"  Confusion  : {confusion_path if confusion_path else 'not found'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two YOLO runs")
    parser.add_argument("--run-a", required=True, help="First run directory")
    parser.add_argument("--run-b", required=True, help="Second run directory")
    parser.add_argument("--label-a", default="YOLO Run A", help="Label for first run")
    parser.add_argument("--label-b", default="YOLO Run B", help="Label for second run")
    parser.add_argument("--output", default="results/run_comparison", help="Output directory for comparison image")
    args = parser.parse_args()

    run_a = Path(args.run_a)
    run_b = Path(args.run_b)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_a = collect_run_summary(run_a)
    summary_b = collect_run_summary(run_b)
    confusion_a = find_confusion_image(run_a)
    confusion_b = find_confusion_image(run_b)

    print_summary(args.label_a, summary_a, confusion_a)
    print_summary(args.label_b, summary_b, confusion_b)

    if confusion_a and confusion_b:
        left = load_image_with_label(confusion_a, args.label_a)
        right = load_image_with_label(confusion_b, args.label_b)
        sheet = build_contact_sheet(left, right)
        out_path = output_dir / "confusion_matrix_comparison.png"
        sheet.save(out_path)
        print(f"\nComparison image saved to: {out_path}")
    else:
        print("\nComparison image not created because one or both confusion matrices are missing.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())