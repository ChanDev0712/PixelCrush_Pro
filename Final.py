import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageGrab
from datetime import datetime
from threading import Thread
import time

images_to_compress = []

def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

# ================= SCAN =================
def scan_folder():
    global images_to_compress
    folder = in_var.get().strip()
    if not folder or not os.path.isdir(folder):
        return

    status.config(text="Scanning...", fg="#00ffff")
    root.update_idletasks()

    exts = ('.jpg','.jpeg','.png','.bmp','.tiff','.tif','.webp','.gif','.avif')
    total = big = small = 0
    total_bytes = 0
    images_to_compress = []
    lines = []
    cut = len(folder) + 1

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
                    lines.append(f"● {rel:<55} | {size:6.2f} MB → COMPRESS")
                else:
                    small += 1
                    lines.append(f"  {rel:<55} | {size:6.2f} MB → skip")

    stat_total.config(text=f"Total: {total:,}")
    stat_big.config(text=f"Compress: {big:,}")
    stat_small.config(text=f"Skip: {small:,}")
    stat_size.config(text=f"Size: {total_bytes/(1024**3):.2f} GB")
    ready_label.config(text=f"→ {big} files → .png (JPG compressed)")

    listbox.delete(0, tk.END)
    for l in lines: listbox.insert(tk.END, l)

    status.config(text=f"Ready! {big} files to crush → .png", fg="#00ff99")
    start_btn.config(state="normal" if big > 0 else "disabled")

# ================= COMPRESS (JPG inside .PNG) =================
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
    except: return False

# ================= START CRUSHING =================
def start_crush():
    if not images_to_compress:
        messagebox.showinfo("PixelCrush Pro", "No files >2MB found!", parent=root)
        return
    out = out_var.get().strip()
    if not out:
        messagebox.showerror("Error", "Select Output Folder!", parent=root)
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
            log.write(f"PIXELCRUSH PRO REPORT ─ {datetime.now():%Y-%m-%d %H:%M}\n")
            log.write(f"Input  → {in_var.get()}\n")
            log.write(f"Output → {out}\n\n")

            for i, src in enumerate(images_to_compress, 1):
                name = os.path.basename(src)
                status.config(text=f"Crushing {i}/{len(images_to_compress)} → {name}")
                prog.set(i / len(images_to_compress) * 100)
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

                elapsed = time.time() - start_t
                speed = i / elapsed if elapsed > 0 else 0
                left = (len(images_to_compress) - i) / speed if speed > 0 else 0
                m, s = divmod(int(left), 60)
                status.config(text=f"● {i}/{len(images_to_compress)} | {speed:.1f}/s | ~{m}m {s}s → .png")

        # Screenshot
        try:
            start_btn.pack_forget()
            root.update()
            ImageGrab.grab(bbox=(root.winfo_rootx(), root.winfo_rooty(),
                                 root.winfo_rootx()+root.winfo_width(),
                                 root.winfo_rooty()+root.winfo_height())).save(sum_png)
            start_btn.pack(pady=25)
        except: pass

        total_t = int(time.time() - start_t)
        status.config(text=f"CRUSHED in {total_t//60}m {total_t%60}s!", fg="#00ff99")
        prog.set(100)
        start_btn.config(state="normal")
        messagebox.showinfo("PIXELCRUSH PRO ✓",
                            f"All Done!\n\n"
                            f"Success: {ok}\n"
                            f"Failed : {fail}\n"
                            f"Time   : {total_t//60}m {total_t%60}s\n\n"
                            f"Log    → {log_file}\n"
                            f"Summary→ {sum_png}", parent=root)

    Thread(target=run, daemon=True).start()

# ================= PIXELCRUSH PRO UI (DARK BLUE) =================
root = tk.Tk()
root.title("PixelCrush Pro ─ JPG → .PNG (<2MB)")
root.geometry("1160x780")
root.configure(bg="#0d1117")

# Safe & Beautiful Fonts
root.option_add("*Font", "Consolas 10")
root.option_add("*Background", "#0d1117")
root.option_add("*Foreground", "#c9d1d9")

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", background="#1f6feb", troughcolor="#161b22", thickness=24)

# Header
tk.Label(root, text="PIXELCRUSH PRO", font=("Arial", 24, "bold"), fg="#58a6ff", bg="#0d1117").pack(pady=(20,10))
tk.Label(root, text="JPG Compression → Saved as .PNG (Max 2MB)", font=("Arial", 11), fg="#8b949e", bg="#0d1117").pack()

# Input
f1 = tk.Frame(root, bg="#0d1117")
f1.pack(fill="x", padx=60, pady=15)
tk.Label(f1, text="IN  :", font=("Arial", 11, "bold"), fg="#58a6ff", bg="#0d1117").pack(side="left")
in_var = tk.StringVar()
tk.Entry(f1, textvariable=in_var, width=80, bg="#21262d", fg="#c9d1d9", insertbackground="#c9d1d9", relief="flat", bd=2).pack(side="left", padx=10, fill="x", expand=True)
tk.Button(f1, text="Browse → Scan", command=lambda: [in_var.set(filedialog.askdirectory() or ""), scan_folder()],
          bg="#238636", fg="white", font=("Arial", 10, "bold"), relief="flat", width=16).pack(side="left", padx=5)

# Output
f2 = tk.Frame(root, bg="#0d1117")
f2.pack(fill="x", padx=60, pady=8)
tk.Label(f2, text="OUT :", font=("Arial", 11, "bold"), fg="#58a6ff", bg="#0d1117").pack(side="left")
out_var = tk.StringVar()
tk.Entry(f2, textvariable=out_var, width=80, bg="#21262d", fg="#c9d1d9", insertbackground="#c9d1d9", relief="flat", bd=2).pack(side="left", padx=10, fill="x", expand=True)
tk.Button(f2, text="Browse", command=lambda: out_var.set(filedialog.askdirectory() or ""),
          bg="#1f6feb", fg="white", font=("Arial", 10, "bold"), relief="flat", width=12).pack(side="left", padx=5)

# Stats
sf = tk.Frame(root, bg="#0d1117")
sf.pack(pady=15)
stat_total = tk.Label(sf, text="Total: 0", font=("Consolas", 12), fg="#8b949e", bg="#0d1117"); stat_total.grid(row=0,column=0,padx=60)
stat_big   = tk.Label(sf, text="Compress: 0", font=("Consolas", 12,"bold"), fg="#ffa657", bg="#0d1117"); stat_big.grid(row=0,column=1,padx=60)
stat_small = tk.Label(sf, text="Skip: 0", font=("Consolas", 12), fg="#7ee787", bg="#0d1117"); stat_small.grid(row=0,column=2,padx=60)
stat_size  = tk.Label(sf, text="Size: 0.00 GB", font=("Consolas", 12), fg="#58a6ff", bg="#0d1117"); stat_size.grid(row=0,column=3,padx=60)

ready_label = tk.Label(root, text="Ready to crush 0 files", font=("Arial", 13, "bold"), fg="#58a6ff", bg="#0d1117")
ready_label.pack(pady=5)

# Listbox
lb = tk.Frame(root, bg="#161b22", relief="flat", bd=2)
lb.pack(fill="both", expand=True, padx=60, pady=12)
listbox = tk.Listbox(lb, font=("Consolas", 10), bg="#161b22", fg="#c9d1d9", selectbackground="#1f6feb")
sb = tk.Scrollbar(lb, command=listbox.yview, bg="#30363d")
listbox.config(yscrollcommand=sb.set)
listbox.pack(side="left", fill="both", expand=True)
sb.pack(side="right", fill="y")

# Progress
prog = tk.DoubleVar()
ttk.Progressbar(root, variable=prog, maximum=100, style="TProgressbar").pack(fill="x", padx=120, pady=20)

# Status
status = tk.Label(root, text="Select input folder", font=("Arial", 11), fg="#8b949e", bg="#0d1117")
status.pack(pady=5)

# START BUTTON
start_btn = tk.Button(root, text="CRUSH ALL →", command=start_crush,
                      bg="#1f6feb", fg="white", font=("Arial", 13, "bold"), height=2, relief="flat", state="disabled")
start_btn.pack(pady=10)

root.mainloop()