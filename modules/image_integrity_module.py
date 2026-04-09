import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageChops # ImageChops ELA için
import os
import numpy as np
import cv2
import threading
from utils.data_storage import data_store

class ImageIntegrityModule:
    def __init__(self, parent_frame, main_app):
        self.parent_frame = parent_frame
        self.main_app = main_app
        self._create_widgets()

    def _create_widgets(self):
        # Kaydırılabilir çerçeve içine yerleştirme
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

        ttk.Label(self.scrollable_frame_inner, text="Görüntü Bütünlüğü ve Orijinallik Doğrulaması", font=("Arial", 14, "bold"), background="#2b2b2b", foreground="white").pack(pady=10)

        # ELA Bölümü
        ela_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Hata Seviyesi Analizi (ELA)", padding=10, style='TFrame')
        ela_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(ela_frame, text="Orijinal Resim:", background="#2b2b2b", foreground="white").pack(side="left", padx=5)
        self.original_image_label = tk.Label(ela_frame, bg="#2b2b2b")
        self.original_image_label.pack(side="left", padx=10, pady=5)

        ttk.Label(ela_frame, text="ELA Haritası:", background="#2b2b2b", foreground="white").pack(side="left", padx=5)
        self.ela_image_label = tk.Label(ela_frame, bg="#2b2b2b")
        self.ela_image_label.pack(side="left", padx=10, pady=5)
        
        self.ela_status_label = ttk.Label(ela_frame, text="Durum: Analiz bekleniyor.", background="#2b2b2b", foreground="white", wraplength=400)
        self.ela_status_label.pack(pady=5)

        # Tersine Resim Arama (Basit Versiyon)
        reverse_search_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Tersine Resim Arama (Basit)", padding=10, style='TFrame')
        reverse_search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(reverse_search_frame, text="Google ile tersine arama yapmak için butona tıklayın.", background="#2b2b2b", foreground="white", wraplength=500).pack(anchor="w")
        self.reverse_search_button = tk.Button(reverse_search_frame, text="Google Görsellerde Ara", command=self._run_reverse_image_search, bg="#007bff", fg="white")
        self.reverse_search_button.pack(pady=5, anchor="w")
        self.reverse_search_results_label = ttk.Label(reverse_search_frame, text="Sonuçlar: Henüz arama yapılmadı.", background="#2b2b2b", foreground="white", wraplength=500)
        self.reverse_search_results_label.pack(anchor="w")

        # Dijital Su İzleme (Placeholder)
        watermarking_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Dijital Su İzleme / Gizli Veri Tespiti", padding=10, style='TFrame')
        watermarking_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(watermarking_frame, text="Bu özellik şu anda sadece placeholder'dır ve geliştirme aşamasındadır.", background="#2b2b2b", foreground="yellow", wraplength=500).pack(anchor="w")
        self.watermarking_status_label = ttk.Label(watermarking_frame, text="Durum: Geliştirme aşamasında.", background="#2b2b2b", foreground="white", wraplength=500)
        self.watermarking_status_label.pack(anchor="w")

    def analyze(self, file_path):
        """
        Görüntü bütünlüğü analizini başlatır.
        """
        self.main_app.status_bar.config(text=f"Görüntü Bütünlüğü Modülü: '{os.path.basename(file_path)}' analiz ediliyor...")
        self._clear_results()
        
        if not file_path or not os.path.exists(file_path) or not file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            self.main_app.status_bar.config(text="Görüntü Bütünlüğü Modülü: Geçersiz resim dosyası.", fg="red")
            return
        
        # Arka planda analiz için thread başlat
        threading.Thread(target=self._run_analysis_in_thread, args=(file_path,)).start()

    def _run_analysis_in_thread(self, file_path):
        results = {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "ela_result": "Analiz Edilemedi",
            "ela_image": None,
            "reverse_search_url": None,
            "watermarking_status": "Geliştirme aşamasında"
        }

        try:
            original_image = Image.open(file_path).convert("RGB")
            results["original_image"] = original_image # GUI için sakla

            # ELA Analizi
            ela_image_pil, ela_status = self._perform_ela(original_image)
            results["ela_result"] = ela_status
            results["ela_image"] = ela_image_pil # PIL Image olarak sakla

        except Exception as e:
            results["ela_result"] = f"ELA hatası: {e}"
            self.main_app.status_bar.config(text=f"Görüntü Bütünlüğü Modülü: ELA hatası: {e}", fg="red")

        # GUI güncellemesini ana thread'de yap
        self.main_app.after(0, lambda: self._update_gui_results(results))
        data_store.add_analysis_result(file_path, "image_integrity", results)
        self.main_app.status_bar.config(text=f"Görüntü Bütünlüğü Modülü: '{os.path.basename(file_path)}' analizi tamamlandı.")

    def _perform_ela(self, image_pil, quality=90, scale=10):
        """
        Error Level Analysis (ELA) gerçekleştirir.
        Bir görüntünün JPEG sıkıştırma kalitesindeki tutarsızlıkları vurgulayarak
        manipülasyonu tespit etmeye çalışır.
        """
        try:
            temp_path = "temp_ela_image.jpg"
            image_pil.save(temp_path, quality=quality)
            recompressed_image = Image.open(temp_path)

            diff = ImageChops.difference(image_pil, recompressed_image)
            
            # Farkı daha görünür hale getirmek için büyüt
            extrema = diff.getextrema()
            max_diff = max([e[1] for e in extrema])
            
            if max_diff == 0:
                ela_image = Image.new('RGB', image_pil.size, (0, 0, 0)) # Siyah resim
                status = "Resim bütünlüğü yüksek, manipülasyon izi bulunamadı."
            else:
                scale_factor = 255.0 / max_diff if max_diff > 0 else 1.0
                ela_image = diff.point(lambda i: i * scale_factor)
                status = "Olası manipülasyon izleri tespit edildi. ELA haritasını inceleyiniz."

            os.remove(temp_path)
            return ela_image, status
        except Exception as e:
            return Image.new('RGB', (100, 100), (0, 0, 0)), f"ELA gerçekleştirilemedi: {e}" # Hata durumunda boş resim

    def _run_reverse_image_search(self):
        """
        Google Görseller ile tersine resim aramasını başlatır.
        Bu, doğrudan API kullanımı yerine tarayıcıyı açarak yapılır,
        çünkü doğrudan API erişimi kısıtlıdır.
        """
        if not self.main_app.current_analysis_file:
            messagebox.showerror("Hata", "Lütfen önce analiz edilecek bir resim seçin.")
            return

        file_path = self.main_app.current_analysis_file
        if not os.path.exists(file_path) or not file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            messagebox.showerror("Hata", "Geçersiz resim dosyası seçildi.")
            return
            
        self.reverse_search_results_label.config(text="Google Görsellerde arama başlatılıyor...")
        
        # Resmi geçici olarak kaydet ve tarayıcıda aç
        try:
            import webbrowser
            import base64
            
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Google'ın tersine resim arama URL'si genellikle bir resmi yüklemeyi veya URL'sini almayı gerektirir.
            # En basit yöntem, resmi bir resim barındırma sitesine yükleyip URL'sini kullanmaktır.
            # Veya doğrudan base64 verisiyle denemek (çoğu tarayıcıda çalışmaz).
            # En güvenilir yol, kullanıcıya manuel yükleme seçeneği sunmaktır.
            # Şimdilik, sadece Google Görselleri açıp kullanıcıdan manuel yüklemesini isteyelim.
            
            webbrowser.open("https://images.google.com/searchbyimage/upload")
            self.reverse_search_results_label.config(text="Google Görseller açıldı. Lütfen resmi manuel olarak yükleyin.")

            # Daha gelişmiş bir çözüm için imbb.com gibi bir yere programatik olarak yükleyip URL'yi kullanmak gerekebilir.
            # Ancak bu, 3. parti API bağımlılığı ve kullanım koşulları getirir.

        except Exception as e:
            self.reverse_search_results_label.config(text=f"Tersine arama başlatılamadı: {e}", foreground="red")
            messagebox.showerror("Hata", f"Tersine arama başlatılamadı: {e}")

    def _clear_results(self):
        """GUI'deki tüm sonuçları temizler."""
        self.original_image_label.config(image=None)
        self.original_image_label.image = None
        self.ela_image_label.config(image=None)
        self.ela_image_label.image = None
        self.ela_status_label.config(text="Durum: Analiz bekleniyor.", foreground="white")
        self.reverse_search_results_label.config(text="Sonuçlar: Henüz arama yapılmadı.", foreground="white")
        self.watermarking_status_label.config(text="Durum: Geliştirme aşamasında.", foreground="white")

    def _update_gui_results(self, results):
        """Analiz sonuçlarını GUI'ye yansıtır."""
        # Orijinal resmi göster
        if results["original_image"]:
            img_pil = results["original_image"]
            img_pil.thumbnail((200, 200))
            tk_img = ImageTk.PhotoImage(img_pil)
            self.original_image_label.config(image=tk_img)
            self.original_image_label.image = tk_img

        # ELA haritasını göster
        if results["ela_image"]:
            ela_img_pil = results["ela_image"]
            ela_img_pil.thumbnail((200, 200))
            tk_ela_img = ImageTk.PhotoImage(ela_img_pil)
            self.ela_image_label.config(image=tk_ela_img)
            self.ela_image_label.image = tk_ela_img
        
        ela_color = "green" if "yüksek" in results["ela_result"] else ("orange" if "olası" in results["ela_result"] else "red")
        self.ela_status_label.config(text=f"Durum: {results['ela_result']}", foreground=ela_color)

        self.main_app.status_bar.config(text=f"Görüntü Bütünlüğü Modülü: '{os.path.basename(results['file_path'])}' analizi tamamlandı.")

    def get_results(self):
        """Bu modülün kaydedilmiş sonuçlarını döndürür."""
        return data_store.get_all_results_for_file(self.main_app.current_analysis_file).get("image_integrity")