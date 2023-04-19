""" Utility functions for generating PDFs through Playwright"""

import json
import pathlib
import tempfile
import time

from playwright.sync_api import sync_playwright

from app import config
from app.api.utils import s3_client
from app.db.models import Atbds
from app.logs import logger  # noqa


def save_pdf_to_s3(local_pdf_path: str, remote_pdf_path: str):
    """
    Uploads a generated PDF from local execution environment to S3
    """
    logger.info("Saving PDF to S3")
    try:
        s3_client().upload_file(
            Filename=local_pdf_path, Bucket=config.S3_BUCKET, Key=remote_pdf_path
        )
    except Exception:
        logger.exception("PDF upload failed.")


def make_pdf(
    atbd_id: int,
    major: str,
    minor: str,
    filepath: str,
    auth_data: dict,
    atbd_alias: str = None,
):
    """
    Generates a PDF for a given ATBD using Playwright
    """
    logger.info("Generating PDF")

    # ATBD PDF preview link to be used by Playwright.
    atbd_link = f"{config.PDF_PREVIEW_HOST}/documents/{atbd_alias if atbd_alias else atbd_id}/v{major}.{minor}/pdf-preview"

    # create a temp directory to store the PDF and related files
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = pathlib.Path(tmp_dir, filepath)
        with sync_playwright() as p:
            # launch a headless browser
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--single-process",
                    "--no-zygote",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ],
                devtools=False,
            )
            # set up the browser context with the localStorage state
            if auth_data:
                storage_state = build_storage_state(
                    tmp_dir,
                    auth_data["user_email"],
                    auth_data["access_token"],
                    auth_data["id_token"],
                )
                context = browser.new_context(storage_state=storage_state)
            else:
                context = browser.new_context()
            page = context.new_page()
            page.goto(atbd_link)
            # wait for a specific marker element to be rendered before generating the PDF
            time.sleep(5)
            page.wait_for_selector("#pdf-preview-ready", state="attached")
            page.pdf(path=local_path, format="A4")
            browser.close()
        logger.info(f"PDF generated at path: {local_path}")
        save_pdf_to_s3(str(local_path), filepath)


def build_storage_state(
    tmp_dir: str, user_email: str, access_token: str, id_token: str
):
    """Set up localStorage state for Playwright

    We store the user's access token and id token in localStorage so that
    the PDF preview page can make authenticated requests to the API.
    """
    # create a temp file with the localStorage state
    temp_file = pathlib.Path(tmp_dir, "storage_state.json")
    temp_file.touch()

    state = {
        "origins": [
            {
                "origin": f"{config.PDF_PREVIEW_HOST}",
                "localStorage": [
                    {
                        "name": f"CognitoIdentityServiceProvider.{config.APP_CLIENT_ID}.LastAuthUser",
                        "value": user_email,
                    },
                    {
                        "name": f"CognitoIdentityServiceProvider.{config.APP_CLIENT_ID}.{user_email}.accessToken",
                        "value": access_token,
                    },
                    {
                        "name": f"CognitoIdentityServiceProvider.{config.APP_CLIENT_ID}.{user_email}.idToken",
                        "value": id_token,
                    },
                ],
            }
        ]
    }
    with open(temp_file, "w") as f:
        json.dump(state, f)
    return temp_file
