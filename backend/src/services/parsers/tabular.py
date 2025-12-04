from typing import List, Dict, Any
import pandas as pd
from src.services.chunking import tabular_to_markdown

def extract_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Read CSV into rows and return a single markdown-like text unit.
    """
    df = pd.read_csv(file_path)
    rows = df.to_dict(orient="records")
    md = tabular_to_markdown(rows)
    return [{"page": 1, "text": md, "sheet": "csv"}]

def extract_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Read XLSX sheets and convert each sheet to markdown-like text unit.
    """
    xls = pd.ExcelFile(file_path)
    units: List[Dict[str, Any]] = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        rows = df.to_dict(orient="records")
        md = tabular_to_markdown(rows)
        units.append({"page": 1, "text": md, "sheet": sheet})
    return units
