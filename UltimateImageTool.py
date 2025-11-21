import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageGrab
from datetime import datetime
from threading import Thread
import time
import shutil

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UltimateImageTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Image Tool Pro")
        self.geometry("1240x820")
        self.images_to_compress = []

        # Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=12)

        self.tabview.add("Compress >2MB → JPG")
        self.tabview.add("Convert All .jpg → .png")

        # ===================== TAB 1: Compress >2MB =====================
        t1 = self.tabview.tab("Compress >2MB → JPG")

        ctk.CTkLabel(t1, text="Compress Images >2MB", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(8, 4))
        ctk.CTkLabel(t1, text="Smart JPEG compression • Log + Screenshot Summary", font=ctk.CTkFont(size=13), text_color="#aaa").pack(pady=(0, 8))

        # Input Row
        in_row = ctk.CTkFrame(t1, corner_radius=8)
        in_row.pack(fill="x", pady=4)
        ctk.CTkLabel(in_row, text="INPUT   ", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        self.input_var1 = ctk.StringVar()
        ctk.CTkEntry(in_row, textvariable=self.input_var1, height=38).grid(row=0, column=1, padx=5, pady=8, sticky="we")
        ctk.CTkButton(in_row, text="Browse → Scan", width=140, height=38, command=self.scan_compress).grid(row=0, column=2, padx=(5, 15), pady=8)
        in_row.grid_columnconfigure(1, weight=1)

        # Output Row
        out_row = ctk.CTkFrame(t1, corner_radius=8)
        out_row.pack(fill="x", pady=4)
        ctk.CTkLabel(out_row, text="OUTPUT  ", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        self.output_var1 = ctk.StringVar()
        ctk.CTkEntry(out_row, textvariable=self.output_var1, height=38).grid(row=0, column=1, padx=5, pady=8, sticky="we")
        ctk.CTkButton(out_row, text="Select Folder", width=140, height=38,
                      command=lambda: self.output_var1.set(filedialog.askdirectory() or "")).grid(row=0, column=2, padx=(5, 15), pady=8)
        out_row.grid_columnconfigure(1, weight=1)

        # Stats
        stats = ctk.CTkFrame(t1, corner_radius=8)
        stats.pack(fill="x", pady=6)
        self.s_total = ctk.CTkLabel(stats, text="Total: 0", font=ctk.CTkFont(size=13))
        self.s_total.grid(row=0, column=0, padx=35, pady=8)
        self.s_large = ctk.CTkLabel(stats, text="To Compress: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff5555")
        self.s_large.grid(row=0, column=1, padx=35, pady=8)
        self.s_skip = ctk.CTkLabel(stats, text="Skip: 0", font=ctk.CTkFont(size=13), text_color="#55ff55")
        self.s_skip.grid(row=0, column=2, padx=35, pady=8)
        self.s_size = ctk.CTkLabel(stats, text="Size: 0 GB", font=ctk.CTkFont(size=13))
        self.s_size.grid(row=0, column=3, padx=35, pady=8)

        self.total_process = ctk.CTkLabel(t1, text="Files to process: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00d4ff")
        self.total_process.pack(pady=6)

        # Listbox
        self.listbox = ctk.CTkTextbox(t1, font=ctk.CTkFont("Consolas", 11), corner_radius=8)
        self.listbox.pack(fill="both", expand=True, pady=6)

        # Progress + Status
        self.progress = ctk.CTkProgressBar(t1, height=22)
        self.progress.pack(fill="x", padx=80, pady=6)
        self.progress.set(0)
        self.status = ctk.CTkLabel(t1, text="Ready", font=ctk.CTkFont(size=13), text_color="#888")
        self.status.pack(pady=2)

        self.btn_compress = ctk.CTkButton(t1, text="START COMPRESSION", height=52, corner_radius=12,
                                          font=ctk.CTkFont(size=23, weight="bold"), state="disabled",
                                          command=self.start_compress)
        self.btn_compress.pack(pady=8)

        # ===================== TAB 2: Convert All .jpg → .png =====================
        t2 = self.tabview.tab("Convert All .jpg → .png")

        ctk.CTkLabel(t2, text="Convert All .jpg → .png", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(8, 4))
        ctk.CTkLabel(t2, text="Simple extension rename • Any file size", font=ctk.CTkFont(size=13), text_color="#aaa").pack(pady=(0, 8))

        # Source Row
        src_row = ctk.CTkFrame(t2, corner_radius=8)
        src_row.pack(fill="x", pady=4)
        ctk.CTkLabel(src_row, text="SOURCE  ", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        self.src_var = ctk.StringVar()
        ctk.CTkEntry(src_row, textvariable=self.src_var, height=38).grid(row=0, column=1, padx=5, pady=8, sticky="we")
        ctk.CTkButton(src_row, text="Browse", width=140, height=38,
                      command=lambda: self.src_var.set(filedialog.askdirectory() or "")).grid(row=0, column=2, padx=(5, 15), pady=8)
        src_row.grid_columnconfigure(1, weight=1)

        # Destination Row
        dst_row = ctk.CTkFrame(t2, corner_radius=8)
        dst_row.pack(fill="x", pady=4)
        ctk.CTkLabel(dst_row, text="DEST     ", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        self.dst_var = ctk.StringVar()
        ctk.CTkEntry(dst_row, textvariable=self.dst_var, height=38).grid(row=0, column=1, padx=5, pady=8, sticky="we")
        ctk.CTkButton(dst_row, text="Browse", width=140, height=38,
                      command=lambda: self.dst_var.set(filedialog.askdirectory() or "")).grid(row=0, column=2, padx=(5, 15), pady=8)
        dst_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(t2, text="START CONVERSION", height=52, corner_radius=12,
                      font=ctk.CTkFont(size=23, weight="bold"), fg_color="#00aa00",
                      command=self.convert_all).pack(pady=8)

        self.result_box = ctk.CTkTextbox(t2, font=ctk.CTkFont("Consolas", 11), corner_radius=8)
        self.result_box.pack(fill="both", expand=True, pady=6)

    # ===================== Compress Functions (Your Original Logic) =====================
    def scan_compress(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.input_var1.set(folder)
        self.images_to_compress.clear()
        self.listbox.delete("0.0", "end")
        self.status.configure(text="Scanning...", text_color="#ffaa00")

        def scan():
            exts = ('.jpg','.jpeg','.png','.bmp','.tiff','.tif','.webp')
            total = large = small = 0
            size_gb = 0
            cut = len(folder) + len(os.path.sep)
            lines = []
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(exts):
                        p = os.path.join(root, f)
                        mb = os.path.getsize(p) / (1024**2)
                        rel = p[cut:]
                        total += 1
                        size_gb += os.path.getsize(p)
                        if mb > 2:
                            large += 1
                            self.images_to_compress.append(p)
                            lines.append(f"{rel} | {mb:6.2f} MB → WILL COMPRESS\n")
                        else:
                            small += 1
                            lines.append(f"{rel} | {mb:6.2f} MB skip (≤2MB)\n")

            self.after(0, lambda: [
                self.s_total.configure(text=f"Total: {total}"),
                self.s_large.configure(text=f"To Compress: {large}"),
                self.s_skip.configure(text=f"Skip: {small}"),
                self.s_size.configure(text=f"Size: {size_gb/(1024**3):.2f}GB"),
                self.total_process.configure(text=f"Files to process: {large}"),
                self.listbox.insert("end", "".join(lines)),
                self.status.configure(text=f"Ready! {large} files", text_color="#00ff00"),
                self.btn_compress.configure(state="normal" if large else "disabled")
            ])

        Thread(target=scan, daemon=True).start()

    def compress_image(self, src, dst):
        try:
            with Image.open(src) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P": img = img.convert("RGBA")
                    bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = bg
                else:
                    img = img.convert("RGB")

                quality = 95
                while quality >= 10:
                    temp = dst + f".temp{quality}.jpg"
                    img.save(temp, "JPEG", quality=quality, optimize=True, progressive=True)
                    if os.path.getsize(temp) <= 2 * 1024 * 1024:
                        os.replace(temp, dst)
                        return True
                    os.remove(temp)
                    quality -= 5
                img.save(dst, "JPEG", quality=10, optimize=True)
                return True
        except Exception as e:
            print(e)
            return False

    def start_compress(self):
        if not self.images_to_compress:
            messagebox.showinfo("Done", "No images need compression!")
            return
        output = self.output_var1.get().strip()
        if not output:
            messagebox.showerror("Error", "Please select Output Folder!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_txt = os.path.join(output, f"Compression_Log_{timestamp}.txt")
        log_png = os.path.join(output, f"Compression_Summary_{timestamp}.png")

        self.btn_compress.configure(state="disabled")
        self.progress.set(0)
        self.status.configure(text="Starting compression...", text_color="#00aaff")

        def run():
            start_time = time.time()
            success = failed = 0

            with open(log_txt, "w", encoding="utf-8") as log:
                log.write(f"IMAGE COMPRESSION REPORT\nDate: {datetime.now()}\nInput: {self.input_var1.get()}\nOutput: {output}\nTotal: {len(self.images_to_compress)}\n\n")

                for i, src in enumerate(self.images_to_compress, 1):
                    filename = os.path.basename(src)
                    rel_dir = os.path.relpath(os.path.dirname(src), self.input_var1.get())
                    dst_dir = os.path.join(output, rel_dir)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, os.path.splitext(filename)[0] + ".jpg")

                    before = os.path.getsize(src) / (1024**2)
                    if self.compress_image(src, dst):
                        after = os.path.getsize(dst) / (1024**2)
                        log.write(f"SUCCESS | {before:6.2f} → {after:6.2f} MB | {os.path.relpath(src, self.input_var1.get())}\n")
                        success += 1
                    else:
                        log.write(f"FAILED | {os.path.relpath(src, self.input_var1.get())}\n")
                        failed += 1

                    percent = i / len(self.images_to_compress)
                    self.progress.set(percent)
                    elapsed = time.time() - start_time
                    speed = i / elapsed if elapsed > 0 else 0
                    remaining = (len(self.images_to_compress) - i) / speed if speed > 0 else 0
                    mins, secs = divmod(int(remaining), 60)
                    eta = f"~{mins}m {secs}s left" if remaining > 0 else "Finishing..."
                    self.status.configure(text=f"{i}/{len(self.images_to_compress)} ({percent:.1%}) • {speed:.1f}/s • {eta}")

            # Screenshot
            try:
                self.btn_compress.pack_forget()
                self.update()
                screenshot = ImageGrab.grab(bbox=(self.winfo_rootx(), self.winfo_rooty(),
                                                 self.winfo_rootx() + self.winfo_width(),
                                                 self.winfo_rooty() + self.winfo_height()))
                screenshot.save(log_png)
                self.btn_compress.pack(pady=8)
            except: pass

            total_time = int(time.time() - start_time)
            self.status.configure(text=f"Finished in {total_time//60}m {total_time%60}s!", text_color="#00ff00")
            self.btn_compress.configure(state="normal")
            messagebox.showinfo("SUCCESS!", f"Compression Complete!\n\nCompressed: {success}\nFailed: {failed}\nTime: {total_time//60}m {total_time%60}s\n\nLog: {log_txt}\nSummary: {log_png}")

        Thread(target=run, daemon=True).start()

    # ===================== Convert All Functions =====================
    def convert_all(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        if not src or not dst:
            messagebox.showwarning("Warning", "Select both folders!")
            return

        self.result_box.delete("0.0", "end")
        self.result_box.insert("end", "Starting conversion...\n")

        def convert():
            count = 0
            for root, _, files in os.walk(src):
                for f in files:
                    if f.lower().endswith(".jpg"):
                        sp = os.path.join(root, f)
                        rel = os.path.relpath(root, src)
                        dp = os.path.join(dst, rel)
                        os.makedirs(dp, exist_ok=True)
                        new_p = os.path.join(dp, os.path.splitext(f)[0] + ".png")
                        shutil.copy(sp, new_p)
                        count += 1
                        self.after(0, lambda p=new_p: self.result_box.insert("end", f"→ {p}\n"))
            self.after(0, lambda: [
                self.result_box.insert("end", f"\nFinished! Converted {count} files."),
                messagebox.showinfo("Done", f"Converted {count} .jpg → .png")
            ])

        Thread(target=convert, daemon=True).start()

if __name__ == "__main__":
    app = UltimateImageTool()
    app.mainloop()