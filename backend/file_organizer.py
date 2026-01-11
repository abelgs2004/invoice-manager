import os
import shutil

def organize_file(original_path: str, fields: dict):
    vendor = fields["vendor"]
    amount = fields["amount"].replace(" ", "")
    date = fields["date"]

    if date != "UNKNOWN":
        day, month, year = date.replace("-", "/").split("/")
    else:
        year, month, day = "unknown", "unknown", "unknown"

    base_dir = f"storage/{year}/{month}/{day}"
    os.makedirs(base_dir, exist_ok=True)

    new_name = f"{year}-{month}-{day}_{vendor}_{amount}.pdf"
    new_path = os.path.join(base_dir, new_name)

    shutil.move(original_path, new_path)
    return new_path
