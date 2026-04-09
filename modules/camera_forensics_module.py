import tkinter as tk
from tkinter import ttk, messagebox
import os
import exifread
import numpy as np
import threading
from utils.data_storage import data_store

class CameraForensicsModule:
    def __init__(self, parent_frame, main_app):
        self.parent_frame = parent_frame
        self.main_app = main_app
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

        ttk.Label(self.scrollable_frame_inner, text="Kamera Özellikleri ve Modeli Tespiti", font=("Arial", 14, "bold"), background="#2b2b2b", foreground="white").pack(pady=10)

        camera_info_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Kamera Bilgisi (EXIF)", padding=10, style='TFrame')
        camera_info_frame.pack(fill="x", padx=10, pady=5)
        self.manufacturer_label = ttk.Label(camera_info_frame, text="Üretici: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.manufacturer_label.pack(anchor="w")
        self.model_label = ttk.Label(camera_info_frame, text="Model: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.model_label.pack(anchor="w")
        self.software_label = ttk.Label(camera_info_frame, text="Yazılım: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.software_label.pack(anchor="w")
        self.lens_model_label = ttk.Label(camera_info_frame, text="Lens Modeli: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.lens_model_label.pack(anchor="w")
        self.focal_length_label = ttk.Label(camera_info_frame, text="Odak Uzaklığı: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.focal_length_label.pack(anchor="w")
        self.exposure_time_label = ttk.Label(camera_info_frame, text="Pozlama Süresi: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.exposure_time_label.pack(anchor="w")
        self.iso_speed_label = ttk.Label(camera_info_frame, text="ISO Hızı: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.iso_speed_label.pack(anchor="w")

        prnu_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="PRNU (Photo Response Non-Uniformity) Analizi", padding=10, style='TFrame')
        prnu_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(prnu_frame, text="PRNU analizi, her sensöre özgü gürültü desenini analiz ederek görüntünün hangi cihazdan geldiğini belirlemeyi amaçlar.", background="#2b2b2b", foreground="white", wraplength=500).pack(anchor="w")
        ttk.Label(prnu_frame, text="Durum: Geliştirme aşamasında. Bu özellik, özel algoritmalar ve bir PRNU veritabanı gerektirir.", background="#2b2b2b", foreground="yellow", wraplength=500).pack(anchor="w", pady=5)
        self.prnu_status_label = ttk.Label(prnu_frame, text="PRNU Statüsü: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.prnu_status_label.pack(anchor="w")
        self.prnu_match_label = ttk.Label(prnu_frame, text="Eşleşen Cihaz ID (PRNU Kimliği): Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.prnu_match_label.pack(anchor="w")
        
        optical_distortion_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Optik Bozulma Analizi", padding=10, style='TFrame')
        optical_distortion_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(optical_distortion_frame, text="Lens bozulmalarını analiz ederek kamera/lens çiftini tanımlama potansiyeli. (Geliştirme aşamasında)", background="#2b2b2b", foreground="yellow", wraplength=500).pack(anchor="w", pady=5)
        self.optical_distortion_label = ttk.Label(optical_distortion_frame, text="Durum: Geliştirme aşamasında.", background="#2b2b2b", foreground="white", wraplength=500)
        self.optical_distortion_label.pack(anchor="w")

    def analyze(self, file_path):
        self.main_app.status_bar.config(text=f"Kamera Adliyesi Modülü: '{os.path.basename(file_path)}' analiz ediliyor...")
        self._clear_results()
        
        if not file_path or not os.path.exists(file_path) or not file_path.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
            self.main_app.status_bar.config(text="Kamera Adliyesi Modülü: Geçersiz resim dosyası.", fg="red")
            return
        
        threading.Thread(target=self._run_analysis_in_thread, args=(file_path,)).start()

    def _run_analysis_in_thread(self, file_path):
        results = {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "manufacturer": "Yok",
            "model": "Yok",
            "software": "Yok",
            "lens_model": "Yok",
            "focal_length": "Yok",
            "exposure_time": "Yok",
            "iso_speed": "Yok",
            "prnu_status": "Geliştirme aşamasında",
            "prnu_match_id": "Yok",
            "optical_distortion_status": "Geliştirme aşamasında"
        }

        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            if tags:
                results["manufacturer"] = str(tags.get('Image Make', 'Yok'))
                results["model"] = str(tags.get('Image Model', 'Yok'))
                results["software"] = str(tags.get('Image Software', 'Yok'))
                results["lens_model"] = str(tags.get('EXIF LensModel', 'Yok'))
                
                focal_length = tags.get('EXIF FocalLength')
                if focal_length: results["focal_length"] = f"{focal_length} mm"

                exposure_time = tags.get('EXIF ExposureTime')
                if exposure_time: results["exposure_time"] = str(exposure_time)

                iso_speed = tags.get('EXIF ISOSpeedRatings')
                if iso_speed: results["iso_speed"] = str(iso_speed)

        except Exception as e:
            self.main_app.status_bar.config(text=f"Kamera Adliyesi Modülü: EXIF okuma hatası: {e}", fg="red")
            results["manufacturer"] = f"Hata: {e}"

        if results["manufacturer"] != "Yok" and results["model"] != "Yok":
            results["prnu_status"] = "PRNU analizi için uygun dosya. Geliştirme aşamasında."
            results["optical_distortion_status"] = "Optik bozulma analizi için uygun dosya. Geliştirme aşamasında."

        self.main_app.after(0, lambda: self._update_gui_results(results))
        data_store.add_analysis_result(file_path, "camera_forensics", results)
        self.main_app.status_bar.config(text=f"Kamera Adliyesi Modülü: '{os.path.basename(file_path)}' analizi tamamlandı.")

    def _clear_results(self):
        self.manufacturer_label.config(text="Üretici: Yok")
        self.model_label.config(text="Model: Yok")
        self.software_label.config(text="Yazılım: Yok")
        self.lens_model_label.config(text="Lens Modeli: Yok")
        self.focal_length_label.config(text="Odak Uzaklığı: Yok")
        self.exposure_time_label.config(text="Pozlama Süresi: Yok")
        self.iso_speed_label.config(text="ISO Hızı: Yok")
        self.prnu_status_label.config(text="PRNU Statüsü: Yok", foreground="white")
        self.prnu_match_label.config(text="Eşleşen Cihaz ID (PRNU Kimliği): Yok", foreground="white")
        self.optical_distortion_label.config(text="Durum: Geliştirme aşamasında.", foreground="white")

    def _update_gui_results(self, results):
        self.manufacturer_label.config(text=f"Üretici: {results['manufacturer']}")
        self.model_label.config(text=f"Model: {results['model']}")
        self.software_label.config(text=f"Yazılım: {results['software']}")
        self.lens_model_label.config(text=f"Lens Modeli: {results['lens_model']}")
        self.focal_length_label.config(text=f"Odak Uzaklığı: {results['focal_length']}")
        self.exposure_time_label.config(text=f"Pozlama Süresi: {results['exposure_time']}")
        self.iso_speed_label.config(text=f"ISO Hızı: {results['iso_speed']}")

        prnu_color = "yellow" if "Geliştirme aşamasında" in results["prnu_status"] else "white"
        self.prnu_status_label.config(text=f"PRNU Statüsü: {results['prnu_status']}", foreground=prnu_color)
        self.prnu_match_label.config(text=f"Eşleşen Cihaz ID (PRNU Kimliği): {results['prnu_match_id']}")
        
        optical_color = "yellow" if "Geliştirme aşamasında" in results["optical_distortion_status"] else "white"
        self.optical_distortion_label.config(text=f"Durum: {results['optical_distortion_status']}", foreground=optical_color)

    def get_results(self):
        return data_store.get_all_results_for_file(self.main_app.current_analysis_file).get("camera_forensics")