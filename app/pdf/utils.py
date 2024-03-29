""" Utility functions for generating PDFs through Playwright"""

import json
import pathlib
import tempfile
import time
from io import BytesIO

import pdfplumber
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

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
    journal: bool = False,
):
    """
    Generates a PDF for a given ATBD using Playwright
    """
    logger.info("Generating PDF")

    # ATBD PDF preview link to be used by Playwright.
    base_url = f"{config.PDF_PREVIEW_HOST}/documents/{atbd_alias if atbd_alias else atbd_id}/v{major}.{minor}"
    if journal:
        atbd_link = f"{base_url}/journal-pdf-preview"
    else:
        atbd_link = f"{base_url}/pdf-preview"

    header_text = "This ATBD was downloaded from the NASA Algorithm Publication Tool (APT) Manuscript submitted to Earth and Space Science."
    header_template = f"""
        <span style="font-size: 8px; color: #D2D4D1; margin: auto; text-align: center;">
            {header_text}
        </span>
    """

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

            # if debugging is enabled, save a screenshot of the page to S3
            if config.FEATURE_FLAGS.get("PDF_EXPORT_DEBUG"):
                logger.info(f"Page URL: {atbd_link}")
                screenshot_filepath = filepath.replace(".pdf", ".png")
                local_screenshot_path = pathlib.Path(tmp_dir, screenshot_filepath)
                page.screenshot(path=local_screenshot_path)
                save_pdf_to_s3(str(local_screenshot_path), screenshot_filepath)
                logger.info(
                    f"Screenshot generated at path: {local_screenshot_path} and saved "
                    f"to S3 at path: {screenshot_filepath}"
                )

            page.wait_for_selector("#pdf-preview-ready", state="attached")
            if journal:
                page.pdf(
                    path=local_path,
                    format="A4",
                    header_template=header_template,
                    footer_template="<span />",
                    prefer_css_page_size=True,
                    display_header_footer=True,
                )
            else:
                page.pdf(path=local_path, format="A4")
            browser.close()

        logger.info(f"PDF generated at path: {local_path}")
        if journal:
            output_pdf_path = str(local_path).replace(".pdf", "_numbered.pdf")
            add_line_numbers(
                str(local_path),
                output_pdf_path,
                ignore_line_texts=set([header_text]),
            )
            save_pdf_to_s3(output_pdf_path, filepath)
        else:
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


def add_line_numbers(input_pdf_path: str, output_pdf_path: str, ignore_line_texts=None):
    """Add line numbers to Journal PDF"""
    logger.info("Adding line numbers to PDF")

    # Load the PDF into PyPDF2 and pdfplumber
    input_pdf = PdfReader(open(input_pdf_path, "rb"))
    plumber_pdf = pdfplumber.open(input_pdf_path)
    line_number = 1
    line_spacing_threshold = 0.1
    # shift the line number up by a few pixels to adjust alignment
    offset = 2

    for page_index, page in enumerate(input_pdf.pages):
        print(f"Processing page {page_index + 1}")
        plumber_page = plumber_pdf.pages[page_index]
        lines = plumber_page.extract_text_lines()
        page_height = plumber_page.height
        packet = BytesIO()
        # Create a new PDF with Reportlab
        can = canvas.Canvas(
            packet, pagesize=(page.mediabox.width, page.mediabox.height)
        )

        # reset previous line bottom on new page
        prev_line_bottom = 0

        for i, line in enumerate(lines):
            if ignore_line_texts and line["text"] in ignore_line_texts:
                continue
            # Coordinates where to write, you can adjust as per your needs
            x = 30
            y = page_height - line["bottom"] + offset
            # If the line is too close to the previous line, skip it
            # This is mostly useful for equations, which are often rendered
            # as multiple lines and pdfplumber gets confused by them and
            # returns multiple lines for a single equation
            line_spacing = line["top"] - prev_line_bottom
            if line_spacing > line_spacing_threshold:
                can.setFont("Helvetica", 7)
                can.drawRightString(x, y, f"{line_number}")
                line_number += 1
            else:
                logger.info(
                    f"Skipping line {i+1} on page {page_index + 1}"
                    f" because it is too close to the previous line"
                    f" (line spacing: {line_spacing})"
                )
            prev_line_bottom = line["bottom"]
        can.save()

        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)
        if new_pdf.pages:  # Sometimes the last page is blank; skip it
            page.merge_page(new_pdf.pages[0])

    # Finally, save the resulting PDF to disk
    output = PdfWriter()
    output.append(input_pdf)
    for page in output.pages:
        # cpu intensive; but reduces file size quite a bit
        page.compress_content_streams()
    output_stream = open(output_pdf_path, "wb")
    output.write(output_stream)
    output_stream.close()
