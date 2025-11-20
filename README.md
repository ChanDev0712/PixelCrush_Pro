# PixelCrush Pro v1.0

**The ultimate bulk image crusher** – Automatically compresses every image >2 MB in a folder (and subfolders) down to ≤2 MB while saving as high-quality `.png` (JPEG inside).

Perfect for portfolios, Shopify/ThemeForest uploads, web assets, or any marketplace that enforces strict 2 MB PNG limits.

[![Download PixelCrush Pro v1.0](https://img.shields.io/github/downloads/ChanDev0712/PixelCrush-Pro/total?style=for-the-badge&color=1f6feb&label=DOWNLOAD%20EXE)](https://github.com/ChanDev0712/PixelCrush-Pro/releases/download/v1.0/PixelCrush_Pro_v1.0.exe)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/ChanDev0712/PixelCrush-Pro/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

## ✨ Features
- Scans entire folder trees instantly
- Skips files already ≤2 MB
- Smart quality reduction (95→10) until file is ≤2 MB
- Handles transparency correctly (white background)
- Preserves original folder structure
- Real-time progress bar + detailed log
- Automatic summary screenshot
- Beautiful dark GitHub-style UI
- Single **portable .exe** – no installation, no Python required

## 🖼️ Supported Input Formats
`.jpg .jpeg .png .bmp .tiff .tif .webp .gif .avif .heic .heif`

→ All converted to optimized **JPEG-inside-PNG** (≤2 MB)

## 🚀 Quick Start (2 clicks)

1. **Download** the exe from the button above  
2. Run `PixelCrush Pro.exe`  
3. Choose **Input** folder → **Scan**  
4. Choose **Output** folder  
5. Click **CRUSH ALL → .PNG**

Done! All images are now under 2 MB and ready to upload.

## 📁 Output
- Crushed images as `.png` (same folder structure)
- `PixelCrush_Log_YYYYMMDD_HHMMSS.txt` – before/after sizes
- `Summary_YYYYMMDD_HHMMSS.png` – screenshot of results

## 🔧 Build from Source (optional)

```bash
git clone https://github.com/ChanDev0712/PixelCrush-Pro.git
cd PixelCrush-Pro
pip install pyinstaller pillow
pyinstaller --onefile --windowed --icon=icon.ico --name="PixelCrush Pro" PixelCrush_Pro.spec
