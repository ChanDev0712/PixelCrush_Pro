import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageGrab
from datetime import datetime
from threading import Thread
import time

# Global list for images >2MB
images_to_compress = []

def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

# ================= SCAN INPUT FOLDER =================
def scan_input_folder():
    global images_to_compress
    folder = input_folder_var.get().strip()
    if not folder or not os.path.isdir(folder):
        return

    status_label.config(text="Scanning folder - please wait...", fg="orange")
    root.update_idletasks()

    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    total_images = large = small = 0
    total_size_bytes = 0
    images_to_compress = []
    display_list = []
    cut_len = len(folder) + len(os.path.sep)

    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(extensions):
                full_path = os.path.join(root_dir, file)
                size_mb = get_file_size_mb(full_path)
                total_images += 1
                total_size_bytes += os.path.getsize(full_path)
                rel_path = full_path[cut_len:]

                if size_mb > 2.0:
                    large += 1
                    images_to_compress.append(full_path)
                    display_list.append(f"{rel_path} | {size_mb:6.2f} MB → WILL COMPRESS")
                else:
                    small += 1
                    display_list.append(f"{rel_path} | {size_mb:6.2f} MB skip (≤2MB)")

    # Update stats
    info_total.config(text=f"Total Images: {total_images}")
    info_large.config(text=f"To Compress (>2MB): {large}", fg="red")
    info_small.config(text=f"Skip (≤2MB): {small}", fg="green")
    info_size.config(text=f"Total Size: {total_size_bytes/(1024**3):.2f} GB")
    total_process_label.config(text=f"Files to process: {large}")

    # Update listbox
    listbox.delete(0, tk.END)
    for line in display_list:
        listbox.insert(tk.END, line)

    status_label.config(text=f"Ready! {large} files will be compressed", fg="green")
    start_button.config(state="normal" if large > 0 else "disabled")

# ================= IMAGE COMPRESSION =================
def compress_image(src_path, dst_path):
    try:
        with Image.open(src_path) as img:
            # Handle transparency
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = bg
            else:
                img = img.convert("RGB")

            quality = 95
            while quality >= 10:
                temp_path = dst_path + f".temp{quality}.jpg"
                img.save(temp_path, "JPEG", quality=quality, optimize=True, progressive=True)
                if get_file_size_mb(temp_path) <= 2.0:
                    os.replace(temp_path, dst_path)
                    return True
                os.remove(temp_path)
                quality -= 5

            # Final save if still big
            img.save(dst_path, "JPEG", quality=10, optimize=True)
            return True
    except Exception as e:
        print(f"Error compressing {src_path}: {e}")
        return False

# ================= START COMPRESSION =================
def start_processing():
    if not images_to_compress:
        messagebox.showinfo("Done", "No images need compression!")
        return

    output_folder = output_folder_var.get().strip()
    if not output_folder:
        messagebox.showerror("Error", "Please select Output Folder!")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_txt_path = os.path.join(output_folder, f"Compression_Log_{timestamp}.txt")
    log_png_path = os.path.join(output_folder, f"Compression_Summary_{timestamp}.png")

    start_button.config(state="disabled")
    progress_var.set(0)
    status_label.config(text="Starting compression...", fg="blue")

    def run_compression():
        start_time = time.time()
        success_count = 0
        failed_count = 0

        with open(log_txt_path, "w", encoding="utf-8") as log:
            log.write(f"IMAGE COMPRESSION REPORT\n")
            log.write(f"Date: {datetime.now()}\n")
            log.write(f"Input Folder: {input_folder_var.get()}\n")
            log.write(f"Output Folder: {output_folder}\n")
            log.write(f"Total to compress: {len(images_to_compress)}\n\n")

            for idx, src in enumerate(images_to_compress, 1):
                filename = os.path.basename(src)
                status_label.config(text=f"Processing {idx}/{len(images_to_compress)}: {filename}")
                percent = (idx / len(images_to_compress)) * 100
                progress_var.set(percent)
                root.update_idletasks()

                rel_dir = os.path.relpath(os.path.dirname(src), input_folder_var.get())
                dst_dir = os_conv = os.path.join(output_folder, rel_dir)
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, os.path.splitext(filename)[0] + ".jpg")

                before = get_file_size_mb(src)
                if compress_image(src, dst):
                    after = get_file_size_mb(dst)
                    log.write(f"SUCCESS | {before:6.2f} → {after:6.2f} MB | {os.path.relpath(src, input_folder_var.get())}\n")
                    success_count += 1
                else:
                    log.write(f"FAILED | {os.path.relpath(src, input_folder_var.get())}\n")
                    failed_count += 1

                # ETA & Speed
                elapsed = time.time() - start_time
                speed = idx / elapsed if elapsed > 0 else 0
                remaining = (len(images_to_compress) - idx) / speed if speed > 0 else 0
                mins, secs = divmod(int(remaining), 60)
                eta_text = f"~{mins}m {secs}s left" if remaining > 0 else "Finishing..."
                status_label.config(text=f"{idx}/{len(images_to_compress)} ({percent:.1f}%) | {speed:.1f} files/sec | {eta_text}")

        # ========= SAVE PNG SUMMARY =========
        try:
            start_button.pack_forget()
            root.update()
            x0 = root.winfo_rootx()
            y0 = root.winfo_rooty()
            x1 = x0 + root.winfo_width()
            y1 = y0 + root.winfo_height()
            screenshot = ImageGrab.grab(bbox=(x0, y0, x1, y1))
            screenshot.save(log_png_path)
            start_button.pack(pady=20)
        except Exception as e:
            print("Screenshot failed:", e)

        total_time = int(time.time() - start_time)
        status_label.config(text=f"Finished in {total_time//60}m {total_time%60}s!", fg="green")
        progress_var.set(100)
        start_button.config(state="normal")

        messagebox.showinfo("SUCCESS!",
                            f"Compression Complete!\n\n"
                            f"Compressed: {success_count}\n"
                            f"Failed: {failed_count}\n"
                            f"Time: {total_time//60}m {total_time%60}s\n\n"
                            f"Text Log Saved:\n{log_txt_path}\n\n"
                            f"PNG Summary Saved:\n{log_png_path}")

    Thread(target=run_compression, daemon=True).start()

# ================= GUI SETUP =================
root = tk.Tk()
root.title("Ultimate Image Compressor Pro")
root.geometry("1000x740")
root.configure(bg="#f4f4f4")

# Input Folder
tk.Label(root, text="INPUT FOLDER", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=(15,5))
input_folder_var = tk.StringVar()
tk.Entry(root, textvariable=input_folder_var, width=110, font=10).pack(pady=5)
tk.Button(root, text="Select Input Folder → Auto Scan", command=lambda: [input_folder_var.set(filedialog.askdirectory() or ""), scan_input_folder()],
          bg="#0066cc", fg="white", font=("Arial", 12, "bold")).pack(pady=8)

# Output Folder
tk.Label(root, text="OUTPUT FOLDER", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=(20,5))
output_folder_var = tk.StringVar()
tk.Entry(root, textvariable=output_folder_var, width=110, font=10).pack(pady=5)
tk.Button(root, text="Select Output Folder", command=lambda: output_folder_var.set(filedialog.askdirectory() or ""),
          font=("Arial", 11)).pack(pady=8)

# Stats Row
stats_frame = tk.Frame(root, bg="#f4f4f4")
stats_frame.pack(pady=10)
info_total = tk.Label(stats_frame, text="Total Images: 0", font=("Arial", 12), bg="#f4f4f4"); info_total.grid(row=0, column=0, padx=30)
info_large = tk.Label(stats_frame, text="To Compress (>2MB): 0", font=("Arial", 12, "bold"), fg="red", bg="#f4f4f4"); info_large.grid(row=0, column=1, padx=30)
info_small = tk.Label(stats_frame, text="Skip (≤2MB): 0", font=("Arial", 12), fg="green", bg="#f4f4f4"); info_small.grid(row=0, column=2, padx=30)
info_size = tk.Label(stats_frame, text="Total Size: 0.00 GB", font=("Arial", 12), bg="#f4f4f4"); info_size.grid(row=0, column=3, padx=30)

total_process_label = tk.Label(root, text="Files to process: 0", font=("Arial", 14, "bold"), fg="darkblue", bg="#f4f4f4")
total_process_label.pack(pady=10)

# Listbox
tk.Label(root, text="All Images (size & action):", font=("Arial", 11), bg="#f4f4f4").pack(anchor="w", padx=30)
list_frame = tk.Frame(root)
list_frame.pack(fill="both", expand=True, padx=25, pady=5)
listbox = tk.Listbox(list_frame, font=("Consolas", 10))
scrollbar = tk.Scrollbar(list_frame, command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)
listbox.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", padx=50, pady=15)

# Status
status_label = tk.Label(root, text="Select input folder to begin", font=("Arial", 12), fg="gray", bg="#f4f4f4")
status_label.pack(pady=5)

# Start Button
start_button = tk.Button(root, text="START COMPRESSION", command=start_processing,
                         bg="#00aa00", fg="white", font=("Arial", 18, "bold"), height=2, state="disabled")
start_button.pack(pady=20)

root.mainloop()