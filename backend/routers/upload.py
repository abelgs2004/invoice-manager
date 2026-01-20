import os
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from starlette.concurrency import run_in_threadpool

from backend.services.pdf_service import extract_text_from_pdf
from backend.services.ocr_service import ocr_image
from backend.services.llm_service import extract_invoice_data_with_llm
from backend.services.field_extractor import extract_fields
from backend.services.drive_service import upload_to_drive
from backend.utils.text_utils import normalize_text, normalize_date, safe_filename
from backend.core.config import STORAGE_ROOT

router = APIRouter()

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    dry_run: bool = False,
    use_custom_name: bool = False,
    provided_vendor: str = Form(None),
    provided_date: str = Form(None),
    provided_amount: str = Form(None)
):
    # 0) Auth Check (Skip for Dry Run if you want unregistered users to try it out)
    creds_json = request.session.get("user_creds")
    if not dry_run and not creds_json:
        raise HTTPException(status_code=401, detail="Authentication required. Please connect Google Drive.")
    # 0) Validate
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, JPG supported")

    # 1) Save temp
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2) Extract text (Still need this for validation or fallback, but could potentially skip if we trust input)
        # However, we'll keep it for now to ensure invalid files aren't processed, 
        # but the main bottleneck is the LLM call below.
        if ext == ".pdf":
            text = await run_in_threadpool(extract_text_from_pdf, temp_path)
        else:
            text = await run_in_threadpool(ocr_image, temp_path)

        text = normalize_text(text)

        if not text or len(text.strip()) < 10:
             # loose check for images which might have less text
             raise HTTPException(status_code=400, detail="Invalid Image/PDF File")

        # 3) Extract fields (Skip LLM if provided)
        rate_limited = False
        if provided_vendor and provided_date and provided_amount:
            print("Using provided fields from frontend, skipping LLM.")
            fields = {
                "vendor": provided_vendor,
                "date": provided_date,
                "amount": provided_amount
            }
        else:
            # LLM First, Regex Fallback
            try:
                fields = await run_in_threadpool(extract_invoice_data_with_llm, text)
            except Exception as e:
                if "429" in str(e):
                    rate_limited = True
                    fields = None
                    print("Rate limit hit, returning specific status.")
                else:
                    fields = None
            
            if not fields:
                if rate_limited and dry_run:
                     # If Dry Run and Rate Limited, abort and tell user to wait
                     # We can't fallback because fallback sucks and confuses user
                     return {
                         "status": "rate_limit",
                         "detail": "AI Service Quota Exceeded. Please wait a moment.",
                         "predicted_filename": f"WAIT_RETRY_{file.filename}"
                     }

                print("LLM failed or unconfigured, using Regex fallback")
                fields = await run_in_threadpool(extract_fields, text)
            else:
                print("LLM Extraction Success!", fields)

        vendor_raw = str(fields.get("vendor", "UNKNOWN"))
        date_raw = str(fields.get("date", "UNKNOWN"))
        amount_raw = str(fields.get("amount", "UNKNOWN"))

        # 4) Normalize date (ALWAYS safe)
        date_norm = date_raw
        if date_norm != "UNKNOWN":
            if not (len(date_norm) == 10 and date_norm[4] == "_" and date_norm[7] == "_"):
                date_norm = normalize_date(date_raw)
        else:
            date_norm = "UNKNOWN"

        # 5) Folder parts from date_norm
        date_pretty = date_raw
        if date_norm != "UNKNOWN":
            try:
                parsed = datetime.strptime(date_norm, "%Y_%m_%d")
                year = parsed.strftime("%Y")
                month = parsed.strftime("%B")  # Use full month name (e.g., "January")
                day = parsed.strftime("%d")
                date_pretty = parsed.strftime("%d %B %Y")
            except Exception:
                year = month = "unknown"
                day = "unknown"
                date_norm = "UNKNOWN"
        else:
            year = month = day = "unknown"

        # 6) Filename Construction
        if use_custom_name:
            # Respect user's custom name (from file.filename)
            # Ensure safe filename just in case but keep user's structure
            # Remove path components to be safe
            final_filename = os.path.basename(file.filename)
            # Optionally sanitize weird chars but keep intention
        else:
            # Auto-generate name: dd Month YYYY_Vendor_Amount.pdf
            safe_vendor = safe_filename(vendor_raw)
            safe_amount = safe_filename(amount_raw)
            if date_norm != "UNKNOWN":
                date_pretty = parsed.strftime("%d %B %Y")
                final_filename = f"{date_pretty}_{safe_vendor}_{safe_amount}{ext}"
            else:
                final_filename = f"UNKNOWN_{safe_vendor}_{safe_amount}{ext}"

        # Safe vendor/amount vars for response (might be undefined if use_custom_name is True)
        # So re-define them for the response object
        safe_vendor = safe_filename(vendor_raw)
        safe_amount = safe_filename(amount_raw)
        
        # --- DRY RUN CHECK ---
        if dry_run:
            # Return analysis only, do not move file or upload to drive
            return {
                "status": "dry_run",
                "fields": {
                    "vendor": vendor_raw,
                    "date": date_pretty,
                    "amount": amount_raw
                },
                "predicted_filename": f"{parsed.strftime('%d %B %Y') if date_norm != 'UNKNOWN' else 'UNKNOWN'}_{safe_vendor}_{safe_amount}{ext}", # Always suggest the auto-name in dry run
                "detail": "Analysis complete. File not saved."
            }

        # 7) Local foldering
        final_dir = os.path.join(STORAGE_ROOT, year, month)
        os.makedirs(final_dir, exist_ok=True)

        final_pdf_path = os.path.join(final_dir, final_filename)
        shutil.move(temp_path, final_pdf_path)

        # 8) Upload to Drive
        drive_links = None
        try:
            drive_links = await run_in_threadpool(
                upload_to_drive,
                local_path=final_pdf_path,
                year=year,
                month=month,
                day=day,
                creds_json=creds_json
            )
        except Exception as e:
            print(f"Drive upload failed: {e}")
            drive_links = None

        # 9) Response
        
        return {
            "status": "success",
            "fields": {
                "vendor": vendor_raw,
                "date": date_pretty,
                "amount": amount_raw
            },
            "normalized": {
                "vendor": safe_vendor,
                "date": date_norm,
                "amount": safe_amount
            },
            "stored_at": final_pdf_path,
            "drive_link": drive_links.get("folder_link") if drive_links else None,
            "file_link": drive_links.get("file_link") if drive_links else None,
            "drive_link_clickable": drive_links.get("folder_link") if drive_links else None
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


    finally:
        # Cleanup temp file if it still exists
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
