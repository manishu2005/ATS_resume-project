# import io
# # import logging

# # try:
# #     from weasyprint import HTML, CSS
# #     WEASYPRINT_INSTALLED = True
# # except ImportError:
# #     WEASYPRINT_INSTALLED = False

# # logger = logging.getLogger('ats_resume_scorer')

# import logging

# logger = logging.getLogger("ats_resume_scorer")

# WEASYPRINT_INSTALLED = False

# try:
#     from weasyprint import HTML, CSS
#     WEASYPRINT_INSTALLED = True
# except (ImportError, OSError) as e:
#     logger.error(f"WeasyPrint unavailable: {e}")
#     HTML = None
#     CSS = None

# def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
#     if not WEASYPRINT_INSTALLED:
#         raise ImportError("WeasyPrint is not installed. PDF generation unavailable.")
        
#     documents = []
    
#     # Render all 3 HTML strings to WeasyPrint Document objects
#     for name, html_str in html_docs.items():
#         doc = HTML(string=html_str).render()
#         documents.append(doc)
    
#     # Merge them into the first document
#     first_doc = documents[0]
#     for other_doc in documents[1:]:
#         for page in other_doc.pages:
#             first_doc.pages.append(page)
            
#     # Write combined PDF bytes
#     pdf_bytes = first_doc.write_pdf()
#     return pdf_bytes


import io
import logging
from xhtml2pdf import pisa

logger = logging.getLogger("ats_resume_scorer")

def _html_to_pdf(html:str)->bytes:
    """Convert a single HTML string to PDF bytes"""
    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(
        src=html,
        dest=pdf_buffer,
        encoding="utf-8"
    )

    if result.err:
        raise RuntimeError("Failed to convert HTML to PDF")
    
    return pdf_buffer.getvalue()

def generate_combined_pdf(html_docs:dit[str, str])->bytes:
    """Convert all HTML reports into a single PDF 
    html_docs example:{
        "summary":"...",
        "skill_report":"...",
        "jd_report":"...",
        "recommendations":"...",

    }
    """
    combined_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page{
                size:A4;
                margin:20mm;
            }
            body{
                font-family:Helvetica, Arial, sans-serif;
                font-size:11pt;
                line-height:1.5;
            }

            .page-break{page-break-after:always;
            }
        </style>
    </head>
    <body>
    """

    total = len(html_docs)

    for index, (_, html) in enumerate(html_docs.items()):
        combined_html += html
        if index < total -1:
            combined_html += '<div class="page-break></div>'
    combined_html += """
    </body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(
        src=combined_html,
        dest=pdf_buffer,
        encoding="utf-8"
    )

    if result.err:
        logger.error("Failed to generate PDF using xhtml2pdf")
        raise RuntimeError("PDF generation failed")
    
    pdf_buffer.seek(0)
    logger.info("PDF generated sucessfully")
    return pdf_buffer.read()
