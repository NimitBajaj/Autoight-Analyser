import sys
import json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    counts_path = Path("data/outputs/demo_run.json")  # adjust if needed
    if not counts_path.exists():
        print(f"❌ No counts file found at {counts_path}")
        sys.exit(1)

    with counts_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats
    if "lights" in data:
        lights = data["lights"]
        legend = data.get("legend", [])
    else:
        # Fallback: assume it's a flat dict of counts
        lights = {k: {"count": v, "category": "Other"} for k, v in data.items()}
        legend = []

    names = list(lights.keys())
    values = [lights[n]["count"] for n in names]

    if not names:
        print("⚠️ No light data found in JSON")
        sys.exit(0)

    # --- Generate Bar Chart ---
    plt.figure(figsize=(8, 5))
    plt.bar(names, values)
    plt.title("Light Counts")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    chart_path = Path("data/outputs/light_counts.png")
    plt.savefig(chart_path)
    plt.close()

    print(f"✅ Chart saved to {chart_path}")

    # --- Generate HTML Report ---
    html_path = Path("data/outputs/light_report.html")
    html_content = f"""
    <html>
    <head><title>Light Report</title></head>
    <body>
      <h1>Light Report</h1>
      <h2>Extracted Legend</h2>
      <ul>{"".join(f"<li>{item}</li>" for item in legend)}</ul>
      <h2>Light Counts</h2>
      <ul>{"".join(f"<li>{name}: {lights[name]['count']} ({lights[name].get('category','Other')})</li>" for name in names)}</ul>
      <h2>Chart</h2>
      <img src="light_counts.png" width="600">
    </body>
    </html>
    """
    html_path.write_text(html_content, encoding="utf-8")
    print(f"✅ HTML report written to {html_path}")

    # --- Generate PDF Report ---
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet

        pdf_path = Path("data/outputs/light_report.pdf")
        doc = SimpleDocTemplate(str(pdf_path))
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("<b>Light Report</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        if legend:
            story.append(Paragraph("<b>Extracted Legend</b>", styles["Heading2"]))
            for item in legend:
                story.append(Paragraph(item, styles["Normal"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph("<b>Light Counts</b>", styles["Heading2"]))
        for name in names:
            story.append(Paragraph(f"{name}: {lights[name]['count']} ({lights[name].get('category','Other')})", styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("<b>Chart</b>", styles["Heading2"]))
        story.append(Image(str(chart_path), width=400, height=250))

        doc.build(story)
        print(f"✅ PDF report written to {pdf_path}")

    except ImportError:
        print("⚠️ reportlab not installed, skipping PDF export.")


if __name__ == "__main__":
    main()