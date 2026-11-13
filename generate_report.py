
from pathlib import Path
import re
import markdown

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image
)

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "reports" / "Final_Project_Report.md"
OUTPUT_FILE = BASE_DIR / "reports" / "Final_Project_Report.pdf"
DASHBOARD = BASE_DIR / "dashboards" / "dashboard.png"

text = INPUT_FILE.read_text(encoding="utf-8")

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="ReportTitle",
    parent=styles["Title"],
    fontSize=20,
    alignment=TA_CENTER,
    textColor=colors.darkblue,
    spaceAfter=20
))

styles.add(ParagraphStyle(
    name="SectionHeading",
    parent=styles["Heading2"],
    fontSize=14,
    textColor=colors.darkblue,
    spaceBefore=15,
    spaceAfter=8
))

styles.add(ParagraphStyle(
    name="ReportBody",
    parent=styles["BodyText"],
    fontSize=10,
    leading=15,
    spaceAfter=8
))

story = []

# Find and remove dashboard image Markdown
image_match = re.search(
    r"!\[.*?\]\((.*?)\)",
    text
)

text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

html = markdown.markdown(text)

parts = re.split(
    r"(<h[1-6]>.*?</h[1-6]>|<p>.*?</p>|<li>.*?</li>|<hr\s*/?>)",
    html
)

for part in parts:
    part = part.strip()

    if not part:
        continue

    heading = re.match(r"<h[1-6]>(.*?)</h[1-6]>", part)
    paragraph = re.match(r"<p>(.*?)</p>", part)
    item = re.match(r"<li>(.*?)</li>", part)

    if heading:
        content = heading.group(1)
        style = styles["ReportTitle"] if not story else styles["SectionHeading"]
        story.append(Paragraph(content, style))

    elif paragraph:
        story.append(Paragraph(paragraph.group(1), styles["ReportBody"]))

    elif item:
        story.append(Paragraph("• " + item.group(1), styles["ReportBody"]))

    elif part.startswith("<hr"):
        story.append(Spacer(1, 10))

# Add actual dashboard image
if DASHBOARD.exists():
    story.append(Spacer(1, 15))
    story.append(Paragraph("E-Commerce Dashboard", styles["SectionHeading"]))

    dashboard_image = Image(str(DASHBOARD))
    dashboard_image._restrictSize(6.8 * inch, 5 * inch)
    story.append(dashboard_image)
else:
    print("Warning: Dashboard image not found!")

# Page numbers
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        A4[0] - 0.6 * inch,
        0.4 * inch,
        f"Page {doc.page}"
    )
    canvas.restoreState()

pdf = SimpleDocTemplate(
    str(OUTPUT_FILE),
    pagesize=A4,
    rightMargin=0.7 * inch,
    leftMargin=0.7 * inch,
    topMargin=0.7 * inch,
    bottomMargin=0.7 * inch
)

pdf.build(
    story,
    onFirstPage=add_page_number,
    onLaterPages=add_page_number
)

print("Final PDF generated successfully!")
print("Saved at:", OUTPUT_FILE)
