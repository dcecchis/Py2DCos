# Py2DCoS  
*A Python tool for two-dimensional correlation spectroscopy analysis & visualisation*

## What is Py2DCoS?

**Py2DCoS** (Python 2-Dimensional Correlation Spectroscopy) brings the power of 2D correlation analysis to the Python ecosystem with a *zero-coding* graphical interface.  
Any system that can be studied by spectroscopy (IR, Raman, NIR, UV-Vis, NMR, etc.) can benefit from 2DCoS to:

- Resolve overlapped spectral bands  
- Reveal subtle perturbation-induced variations  
- Distinguish synchronous vs. asynchronous behaviours  
- Extract kinetics or structural information unavailable in 1D spectra  

Key features
------------

| Category | Highlights |
|----------|------------|
| **GUI**  | Point-and-click loading of CSV / Excel / TXT files, real-time sliders, colormap & contour controls |
| **Pre-processing** | PCA reconstruction, Gaussian smoothing, node-attenuation filter |
| **Computation** | Synchronous & asynchronous maps via Hilbert transform (HT) |
| **Visualisation** | Matplotlib 2D maps with interactive colour-bar, diagonal/anti-diagonal selection, 3-D Plotly surfaces |
| **Formats** | Excel (select sheet/column ranges), comma-/tab-separated text, plain CSV |
| **Export** | Save figures, PCA reports, correlograms, scores plots |

---

## Installation

Install from the repository:

```bash
git clone https://github.com/dcecchis/Py2DCos
cd Py2DCos
pip install .
```
## Requirements

Python ≥ 3.10 and the following Python packages (installed automatically with `pip install .`): `numpy`, `scipy`, `matplotlib`, `pandas`, `PyQt5`, `plotly`, `openpyxl`.

## Quick Start

### Launch the graphical interface

```bash
py2dcos --gui
```
1. **Load data** – choose your CSV, TXT, or XLSX file(s)

2. **Select reference spectrum** – zero, mean, initial, final, etc.

3. **(Optional) Preprocessing** – PCA reconstruction, Gaussian σ slider, node-attenuation checkbox

4. **Plot** – click Plot to display synchronous / asynchronous / both maps

5. **Explore** – adjust contour number, colours, diagonal/anti-diagonal, and intensity sliders in real time

### Command-line mode
Currently Py2DCoS is GUI-centric. The command below simply launches the interface.
```bash
py2dcos --gui
```

## Citation
If Py2DCoS contributes to your research, please cite: 