# ================= PIXELCRUSH PRO v1.0 - FULL FINAL CODE =================
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageGrab
from datetime import datetime
from threading import Thread
import time

# ---------- PYINSTALLER ICON FIX ----------
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- GLOBAL ----------
images_to_compress = []

def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

# ---------- SCAN FOLDER ----------
def scan_folder():
    global images_to_compress
    folder = in_var.get().strip()
    if not folder or not os.path.isdir(folder):
        return

    status.config(text="Scanning folder...", fg="#00ffff")
    root.update_idletasks()

    exts = ('.jpg','.jpeg','.png','.bmp','.tiff','.tif','.webp','.gif','.avif','.heic','.heif')
    total = big = small = 0
    total_bytes = 0
    images_to_compress = []
    lines = []
    cut = len(folder) + len(os.path.sep)

    for r, _, f in os.walk(folder):
        for file in f:
            if file.lower().endswith(exts):
                path = os.path.join(r, file)
                size = get_file_size_mb(path)
                total += 1
                total_bytes += os.path.getsize(path)
                rel = path[cut:]

                if size > 2.0:
                    big += 1
                    images_to_compress.append(path)
                    lines.append(f"● {rel} | {size:6.2f} MB → COMPRESS")
                else:
                    small += 1
                    lines.append(f"  {rel} | {size:6.2f} MB → skip")

    stat_total.config(text=f"Total: {total:,}")
    stat_big.config(text=f"Compress: {big:,}")
    stat_small.config(text=f"Skip: {small:,}")
    stat_size.config(text=f"Size: {total_bytes/(1024**3):.2f} GB")
    ready_label.config(text=f"→ {big} files → .png (JPG compressed)")

    listbox.delete(0, tk.END)
    for l in lines:
        listbox.insert(tk.END, l)

    status.config(text=f"Ready! {big} files ready", fg="#00ff99")
    start_btn.config(state="normal" if big > 0 else "disabled")

# ---------- COMPRESSION ENGINE ----------
def crush_image(src, dst):
    try:
        with Image.open(src) as im:
            if im.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", im.size, (255,255,255))
                if im.mode == "P": im = im.convert("RGBA")
                bg.paste(im, mask=im.split()[-1] if "A" in im.mode else None)
                im = bg
            else:
                im = im.convert("RGB")

            q = 95
            while q >= 10:
                tmp = dst + f".tmp{q}"
                im.save(tmp, "JPEG", quality=q, optimize=True, progressive=True)
                if get_file_size_mb(tmp) <= 2.0:
                    os.replace(tmp, dst)
                    return True
                os.remove(tmp)
                q -= 5
            im.save(dst, "JPEG", quality=10, optimize=True)
            return True
    except:
        return False

# ---------- START CRUSHING ----------
def start_crush():
    if not images_to_compress:
        messagebox.showinfo("PixelCrush Pro", "No files >2MB found!")
        return
    out = out_var.get().strip()
    if not out:
        messagebox.showerror("Error", "Select Output Folder!")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(out, f"PixelCrush_Log_{ts}.txt")
    sum_png = os.path.join(out, f"Summary_{ts}.png")

    start_btn.config(state="disabled")
    prog.set(0)
    status.config(text="Crushing images...", fg="#00ddff")

    def run():
        start_t = time.time()
        ok = fail = 0

        with open(log_file, "w", encoding="utf-8") as log:
            log.write(f"PIXELCRUSH PRO v1.0 - {datetime.now():%Y-%m-%d %H:%M}\n")
            log.write(f"Input  → {in_var.get()}\n")
            log.write(f"Output → {out}\n\n")

            for i, src in enumerate(images_to_compress, 1):
                name = os.path.basename(src)
                status.config(text=f"Crushing {i}/{len(images_to_compress)} → {name}")
                prog.set((i / len(images_to_compress)) * 100)
                root.update_idletasks()

                rel_dir = os.path.relpath(os.path.dirname(src), in_var.get())
                dst_dir = os.path.join(out, rel_dir)
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, os.path.splitext(name)[0] + ".png")

                before = get_file_size_mb(src)
                if crush_image(src, dst):
                    after = get_file_size_mb(dst)
                    log.write(f"✓ {before:6.2f} → {after:6.2f} MB | {os.path.basename(dst)}\n")
                    ok += 1
                else:
                    log.write(f"✗ FAILED | {name}\n")
                    fail += 1

        # Screenshot summary
        try:
            start_btn.pack_forget()
            root.update()
            ImageGrab.grab(bbox=(root.winfo_rootx(), root.winfo_rooty(),
                                 root.winfo_rootx() + root.winfo_width(),
                                 root.winfo_rooty() + root.winfo_height())).save(sum_png)
            start_btn.pack(pady=30)
        except: pass

        total_t = int(time.time() - start_t)
        status.config(text=f"CRUSHED in {total_t//60}m {total_t%60}s!", fg="#00ff99")
        prog.set(100)
        start_btn.config(state="normal")
        messagebox.showinfo("PixelCrush Pro ✓",
                            f"All Done!\n\nSuccess: {ok}\nFailed : {fail}\nTime   : {total_t//60}m {total_t%60}s\n\nLog → {log_file}")

    Thread(target=run, daemon=True).start()

# ---------- GUI ----------
root = tk.Tk()
root.title("PixelCrush Pro v1.0")

# SET ICON (works in .py and .exe)
icon_path = resource_path("icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

root.geometry("1160x780")
root.configure(bg="#0d1117")

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", background="#1f6feb", troughcolor="#161b22", thickness=26)

# Header
tk.Label(root, text="PIXELCRUSH PRO", font=("Arial", 26, "bold"), fg="#58a6ff", bg="#0d1117").pack(pady=(20,8))
tk.Label(root, text="JPG Compression → Saved as .PNG (<2MB)", font=("Arial", 11), fg="#8b949e", bg="#0d1117").pack()

# Input & Output
for label, var, btn_text, cmd, color in [
    ("IN  :", in_var := tk.StringVar(), "Browse → Scan", lambda: [in_var.set(filedialog.askdirectory() or ""), scan_folder()], "#238636"),
    ("OUT :", out_var := tk.StringVar(), "Browse", lambda: out_var.set(filedialog.askdirectory() or ""), "#1f6feb")
]:
    f = tk.Frame(root, bg="#0d1117")
    f.pack(fill="x", padx=60, pady=10)
    tk.Label(f, text=label, font=("Arial", 11, "bold"), fg="#58a6ff", bg="#0d1117").pack(side="left")
    tk.Entry(f, textvariable=var, width=82, bg="#21262d", fg="#c9d1d9", insertbackground="#c9d1d9", relief="flat", bd=2).pack(side="left", padx=10, fill="x", expand=True)
    tk.Button(f, text=btn_text, command=cmd, bg=color, fg="white", font=("Arial", 10, "bold"), relief="flat", width=16).pack(side="left", padx=5)

# Stats
sf = tk.Frame(root, bg="#0d1117")
sf.pack(pady=15)
stat_total = tk.Label(sf, text="Total: 0", font=("Consolas", 12), fg="#8b949e", bg="#0d1117"); stat_total.grid(row=0,column=0,padx=70)
stat_big   = tk.Label(sf, text="Compress: 0", font=("Consolas", 12,"bold"), fg="#ffa657", bg="#0d1117"); stat_big.grid(row=0,column=1,padx=70)
stat_small = tk.Label(sf, text="Skip: 0", font=("Consolas", 12), fg="#7ee787", bg="#0d1117"); stat_small.grid(row=0,column=2,padx=70)
stat_size  = tk.Label(sf, text="Size: 0.00 GB", font=("Consolas", 12), fg="#58a6ff", bg="#0d1117"); stat_size.grid(row=0,column=3,padx=70)

ready_label = tk.Label(root, text="Ready to crush 0 files", font=("Arial", 13, "bold"), fg="#58a6ff", bg="#0d1117")
ready_label.pack(pady=5)

# Listbox
lb = tk.Frame(root, bg="#161b22", bd=2, relief="flat")
lb.pack(fill="both", expand=True, padx=60, pady=12)
listbox = tk.Listbox(lb, font=("Consolas", 10), bg="#161b22", fg="#c9d1d9", selectbackground="#1f6feb")
sb = tk.Scrollbar(lb, command=listbox.yview)
listbox.config(yscrollcommand=sb.set)
listbox.pack(side="left", fill="both", expand=True)
sb.pack(side="right", fill="y")

# Progress & Status
prog = tk.DoubleVar()
ttk.Progressbar(root, variable=prog, style="TProgressbar").pack(fill="x", padx=130, pady=20)
status = tk.Label(root, text="Select input folder", font=("Arial", 11), fg="#8b949e", bg="#0d1117")
status.pack(pady=5)

# Start Button
start_btn = tk.Button(root, text="CRUSH ALL → .PNG", command=start_crush,
                      bg="#1f6feb", fg="white", font=("Arial", 13, "bold"), height=2, relief="flat", state="disabled")
start_btn.pack(pady=10)

root.mainloop()