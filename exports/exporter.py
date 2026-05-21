# exports/exporter.py
# ─────────────────────────────────────────────────────────────
# Saves scraped data and failure logs to flat files.
# All three formats (JSON, CSV, XML) are built into Python —
# no extra libraries needed.
#
# Functions:
#   save_json(data)      → result.json
#   save_csv(data)       → result.csv
#   save_xml(data)       → result.xml
#   save_failures(data)  → failed_urls.json
# ─────────────────────────────────────────────────────────────

import json
import csv
import xml.etree.ElementTree as ET
from typing import List, Dict

from utils.logger import logger


def save_json(data: List[Dict], path: str = "result.json"):
    """Save data as a nicely formatted JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved JSON → {path}")


def save_csv(data: List[Dict], path: str = "result.csv"):
    """
    Save data as a CSV file.
    encoding="utf-8-sig" adds a BOM so Excel opens it correctly
    without scrambling Japanese characters.
    """
    if not data:
        logger.warning("No data to save as CSV.")
        return

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Saved CSV  → {path}")


def save_xml(data: List[Dict], path: str = "result.xml"):
    """Save data as an XML file, one <salon> element per row."""
    root = ET.Element("salons")

    for item in data:
        salon_el = ET.SubElement(root, "salon")
        for key, val in item.items():
            child = ET.SubElement(salon_el, key)
            child.text = str(val) if val is not None else ""

    # ET.indent adds nice indentation so the file is human-readable
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    logger.info(f"Saved XML  → {path}")


def save_failures(failures: List[Dict], path: str = "failed_urls.json"):
    """Save the list of failed URLs so you can investigate them later."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(failures, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved failures → {path}  ({len(failures)} entries)")
