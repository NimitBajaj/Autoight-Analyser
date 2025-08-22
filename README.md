# AutoLight Analyser

This project demonstrates an **automated pipeline** for extracting lighting-related information from AutoCAD exports (DXF/TXT), cleaning up legends, counting occurrences of lighting symbols, and generating **client-friendly reports** with charts.

---

## 📦 Features

- Extract **legend items** from raw DXF text dumps
- Normalize light names (e.g. `PENDENT LIGHT` → `Pendant Light`)
- Categorize lights into **Hanging / Track / Indirect / Recessed / Other**
- Count occurrences of each light type in the drawing text
- Generate **visual reports**:
  - JSON summary
  - PNG bar chart
  - HTML report (interactive-friendly)
  - PDF report (client-ready)

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Autoight-Analyser.git
cd Autoight-Analyser

```
