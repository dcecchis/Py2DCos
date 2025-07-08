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
| **Computation** | Synchronous & asynchronous maps via Hilbert transform (HT) *(FFT coming soon)* |
| **Visualisation** | Matplotlib 2D maps with interactive colour-bar, diagonal/anti-diagonal selection, 3-D Plotly surfaces |
| **Formats** | Excel (select sheet/column ranges), comma-/tab-separated text, plain CSV |
| **Export** | Save figures, PCA reports, correlograms, scores plots |

---

## ⚙️ Installation

Py2DCoS will soon be on PyPI. For now, install from the repository:

```bash
git clone https://github.com/dcecchis/Py2DCos
cd Py2DCos
pip install .