import os
import shutil
from datetime import datetime

def organize_file(original_path: str, fields: dict):
    vendor = fields["vendor"]
    amount = fields["amount"].replace(" ", "")
    date = fields["date"]

    if date != "UNKNOWN":
        try:
            # Assumes YYYY_MM_DD or YYYY-MM-DD
            dt = datetime.strptime(date.replace("-", "_"), "%Y_%m_%d")
            year = dt.strftime("%Y")
            month = dt.strftime("%B")
            day = dt.strftime("%d")
            date_pretty = dt.strftime("%d %B %Y")
        except:
            year, month, day, date_pretty = "unknown", "unknown", "unknown", "UNKNOWN"
    else:
        year, month, day, date_pretty = "unknown", "unknown", "unknown", "UNKNOWN"

    from backend.utils.text_utils import safe_filename
    safe_v = safe_filename(vendor)
    safe_a = safe_filename(amount)

    base_dir = os.path.join("storage", year, month)
    os.makedirs(base_dir, exist_ok=True)

    ext = os.path.splitext(original_path)[1].lower()
    new_name = f"{date_pretty}_{safe_v}_{safe_a}{ext}"
    new_path = os.path.join(base_dir, new_name)

    shutil.move(original_path, new_path)
    return new_path
