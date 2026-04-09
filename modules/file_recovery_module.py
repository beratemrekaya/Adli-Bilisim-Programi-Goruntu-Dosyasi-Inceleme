import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
from utils.data_storage import data_store
from utils.file_operations import ensure_directory_exists

class FileRecoveryModule:
    def __init__(self, parent_frame, main_app):
        self.parent_frame = parent_frame
        self.main_app = main_app
        self.output_dir = "recovered_files"
        ensure_directory_exists(self.output_dir)
        self._create_widgets()

    def _create_widgets(self):
        self.scroll_frame = tk.Frame(self.parent_frame, bg="#2b2b2b")
        self.scroll_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.scroll_frame, bg="#2b2b2b", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame_inner = ttk.Frame(self.canvas, style='TFrame')

        self.scrollable_frame_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        ttk.Label(self.scrollable_frame_inner, text="Silinmiş Dosya İzi ve Geçici Veri Kurtarma", font=("Arial", 14, "bold"), background="#2b2b2b", foreground="white").pack(pady=10)

        thumbnail_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Thumbnail/Önizleme Kurtarma", padding=10, style='TFrame')
        thumbnail_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(thumbnail_frame, text="Sistem ve uygulamaların oluşturduğu önizleme/thumbnail dosyalarını tarar.", background="#2b2b2b", foreground="white", wraplength=500).pack(anchor="w")
        
        ttk.Label(thumbnail_frame, text="Tarama Dizini:", background="#2b2b2b", foreground="white").pack(side="left", padx=5)
        self.thumbnail_scan_path_entry = ttk.Entry(thumbnail_frame, width=50)
        self.thumbnail_scan_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.thumbnail_scan_path_entry.insert(0, os.path.expanduser("~"))
        
        select_dir_button = tk.Button(thumbnail_frame, text="Dizin Seç", command=self._select_scan_directory, bg="#007bff", fg="white")
        select_dir_button.pack(side="left", padx=5)

        scan_button = tk.Button(thumbnail_frame, text="Taramayı Başlat", command=self._start_thumbnail_scan, bg="#5cb85c", fg="white")
        scan_button.pack(pady=5, anchor="w")
        
        self.thumbnail_results_label = ttk.Label(thumbnail_frame, text="Durum: Taramayı bekliyor.", background="#2b2b2b", foreground="white", wraplength=500)
        self.thumbnail_results_label.pack(anchor="w")
        
        tk.Label(thumbnail_frame, text="Bulunan Thumbnail'lar:", background="#2b2b2b", foreground="white").pack(anchor="w", pady=5)
        self.thumbnail_listbox = tk.Listbox(thumbnail_frame, bg="#4a4a4a", fg="white", selectbackground="#007acc", relief="flat", bd=0, height=8)
        self.thumbnail_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.thumbnail_listbox.bind("<Double-Button-1>", self._open_recovered_file)

        deleted_file_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Silinmiş Dosya İzi Arama", padding=10, style='TFrame')
        deleted_file_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(deleted_file_frame, text="Bu özellik, silinmiş dosyaların dosya sistemi üzerindeki izlerini bulmaya odaklanır. Doğrudan disk okuma yetenekleri ve işletim sistemi ayrıcalıkları gerektirdiğinden, bu Python uygulaması kapsamında tam bir dosya kurtarma aracı olarak tasarlanmamıştır.", background="#2b2b2b", foreground="white", wraplength=500).pack(anchor="w")
        ttk.Label(deleted_file_frame, text="Durum: Geliştirme aşamasında. Linux'ta `/dev/sdX` gibi ham disk cihazlarını okuyabilir, ancak Windows'ta bu daha zordur.", background="#2b2b2b", foreground="yellow", wraplength=500).pack(anchor="w", pady=5)
        self.deleted_file_status_label = ttk.Label(deleted_file_frame, text="Durum: Geliştirme aşamasında.", background="#2b2b2b", foreground="white", wraplength=500)
        self.deleted_file_status_label.pack(anchor="w")

    def analyze(self, file_path=None):
        self.main_app.status_bar.config(text=f"Dosya Kurtarma Modülü: Analiz başlatılıyor...")
        self._clear_results()
        self.main_app.status_bar.config(text=f"Dosya Kurtarma Modülü: Beklemede. Lütfen tarama başlatın.")

    def _select_scan_directory(self):
        directory = filedialog.askdirectory(title="Tarama Dizini Seç")
        if directory:
            self.thumbnail_scan_path_entry.delete(0, tk.END)
            self.thumbnail_scan_path_entry.insert(0, directory)

    def _start_thumbnail_scan(self):
        scan_dir = self.thumbnail_scan_path_entry.get()
        if not os.path.isdir(scan_dir):
            messagebox.showerror("Hata", "Geçersiz tarama dizini.")
            return

        self.main_app.status_bar.config(text=f"Dosya Kurtarma Modülü: '{scan_dir}' dizininde thumbnail taranıyor...")
        self.thumbnail_results_label.config(text="Durum: Tarama devam ediyor...", foreground="orange")
        self.thumbnail_listbox.delete(0, tk.END)

        threading.Thread(target=self._scan_for_thumbnails_in_thread, args=(scan_dir,)).start()

    def _scan_for_thumbnails_in_thread(self, scan_dir):
        found_thumbnails = []
        thumbnail_paths = [
            os.path.join(os.path.expanduser("~"), ".cache", "thumbnails", "normal"),
            os.path.join(os.path.expanduser("~"), ".cache", "thumbnails", "large"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Microsoft", "Windows", "Explorer"),
        ]
        
        thumbnail_paths.insert(0, scan_dir)

        thumbnail_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        
        unique_thumbnails = set()

        for base_path in thumbnail_paths:
            if not os.path.exists(base_path):
                continue
            
            for root, _, files in os.walk(base_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in thumbnail_extensions):
                        full_path = os.path.join(root, file)
                        if full_path not in unique_thumbnails:
                            found_thumbnails.append(full_path)
                            unique_thumbnails.add(full_path)
        
        self.main_app.after(0, lambda: self._update_thumbnail_results(found_thumbnails))
        
        data_store.add_analysis_result(scan_dir, "file_recovery_thumbnails", {
            "scanned_directory": scan_dir,
            "found_count": len(found_thumbnails),
            "found_files": found_thumbnails
        })
        self.main_app.status_bar.config(text=f"Dosya Kurtarma Modülü: Thumbnail taraması tamamlandı. {len(found_thumbnails)} dosya bulundu.")

    def _update_thumbnail_results(self, found_thumbnails):
        self.thumbnail_listbox.delete(0, tk.END)
        if found_thumbnails:
            for thumb_path in found_thumbnails:
                self.thumbnail_listbox.insert(tk.END, thumb_path)
            self.thumbnail_results_label.config(text=f"Durum: {len(found_thumbnails)} adet thumbnail bulundu.", foreground="green")
        else:
            self.thumbnail_results_label.config(text="Durum: Thumbnail bulunamadı.", foreground="orange")

    def _open_recovered_file(self, event):
        selected_indices = self.thumbnail_listbox.curselection()
        if selected_indices:
            file_path = self.thumbnail_listbox.get(selected_indices[0])
            if os.path.exists(file_path):
                try:
                    os.startfile(file_path)
                except AttributeError:
                    import subprocess
                    subprocess.call(['xdg-open', file_path])
                except Exception as e:
                    messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı veya silindi.")

    def _clear_results(self):
        self.thumbnail_results_label.config(text="Durum: Taramayı bekliyor.", foreground="white")
        self.thumbnail_listbox.delete(0, tk.END)
        self.deleted_file_status_label.config(text="Durum: Geliştirme aşamasında.", foreground="white")

    def get_results(self):
        return data_store.get_analysis_result(self.thumbnail_scan_path_entry.get(), "file_recovery_thumbnails")