import tkinter as tk
from tkinter import ttk, messagebox
import os
import exifread # Resim EXIF verileri için
import piexif # EXIF yazma/düzenleme potansiyeli için (manipülasyon tespiti)
from datetime import datetime
from geopy.geocoders import Nominatim # Koordinattan adrese çevirme için
import threading
from utils.data_storage import data_store
import subprocess # mediainfo CLI aracı için
import json # mediainfo'nun JSON çıktısını işlemek için

class MetadataAnalysisModule:
    def __init__(self, parent_frame, main_app):
        self.parent_frame = parent_frame
        self.main_app = main_app
        self.geolocator = Nominatim(user_agent="forensics_tool_app") # GeoLocator başlatma
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
        
        # Meta Veri Başlığı
        ttk.Label(self.scrollable_frame_inner, text="Meta Veri Analizi ve Manipülasyon Tespiti", font=("Arial", 14, "bold"), background="#2b2b2b", foreground="white").pack(pady=10)

        # Temel Meta Veriler
        self.basic_metadata_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Temel Meta Veriler", padding=10, style='TFrame')
        self.basic_metadata_frame.pack(fill="x", padx=10, pady=5)
        self.creation_date_label = ttk.Label(self.basic_metadata_frame, text="Oluşturma Tarihi: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.creation_date_label.pack(anchor="w")
        self.modification_date_label = ttk.Label(self.basic_metadata_frame, text="Değiştirme Tarihi: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.modification_date_label.pack(anchor="w")
        self.file_size_label = ttk.Label(self.basic_metadata_frame, text="Dosya Boyutu: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.file_size_label.pack(anchor="w")
        self.camera_model_label = ttk.Label(self.basic_metadata_frame, text="Kamera Modeli: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.camera_model_label.pack(anchor="w")
        self.software_label = ttk.Label(self.basic_metadata_frame, text="Yazılım: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.software_label.pack(anchor="w")

        # Konum Verileri
        self.location_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Konum Verileri (GPS)", padding=10, style='TFrame')
        self.location_frame.pack(fill="x", padx=10, pady=5)
        self.gps_coords_label = ttk.Label(self.location_frame, text="GPS Koordinatları: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.gps_coords_label.pack(anchor="w")
        self.address_label = ttk.Label(self.location_frame, text="Tahmini Adres: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.address_label.pack(anchor="w")

        # Manipülasyon Tespiti
        self.manipulation_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Manipülasyon Tespiti", padding=10, style='TFrame')
        self.manipulation_frame.pack(fill="x", padx=10, pady=5)
        self.manipulation_warning_label = ttk.Label(self.manipulation_frame, text="Durum: Analiz bekleniyor.", background="#2b2b2b", foreground="yellow", font=("Arial", 10, "bold"), wraplength=500)
        self.manipulation_warning_label.pack(anchor="w")
        self.meta_date_consistency_label = ttk.Label(self.manipulation_frame, text="Meta Veri Tarih Tutarlılığı: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.meta_date_consistency_label.pack(anchor="w")
        self.exif_integrity_label = ttk.Label(self.manipulation_frame, text="EXIF Bütünlüğü: Yok", background="#2b2b2b", foreground="white", wraplength=500)
        self.exif_integrity_label.pack(anchor="w")

        # Tüm Meta Veriler (Genişletilebilir)
        self.all_metadata_frame = ttk.LabelFrame(self.scrollable_frame_inner, text="Tüm Ham Meta Veriler", padding=10, style='TFrame')
        self.all_metadata_frame.pack(fill="x", padx=10, pady=5)
        self.all_metadata_text = tk.Text(self.all_metadata_frame, wrap="word", height=10, bg="#4a4a4a", fg="white", bd=0, relief="flat")
        self.all_metadata_text.pack(fill="both", expand=True)
        self.all_metadata_text.config(state="disabled") # Salt okunur

    def analyze(self, file_path):
        """
        Belirtilen dosyanın meta verilerini analiz eder.
        """
        self.main_app.status_bar.config(text=f"Meta Veri Modülü: '{os.path.basename(file_path)}' analiz ediliyor...")
        # Önceki sonuçları temizle
        self._clear_results()
        
        # Arka planda analiz için thread başlat
        threading.Thread(target=self._run_analysis_in_thread, args=(file_path,)).start()

    def _run_analysis_in_thread(self, file_path):
        results = {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "creation_date": "Yok",
            "modification_date": "Yok",
            "file_size": f"{os.path.getsize(file_path)} bytes",
            "camera_model": "Yok",
            "software": "Yok",
            "gps_coordinates": "Yok",
            "estimated_address": "Yok",
            "manipulation_warnings": [],
            "raw_metadata": {}
        }
        
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
            try:
                with open(file_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False) # details=False daha hızlı
                    
                if tags:
                    results["raw_metadata"] = {str(k): str(v) for k, v in tags.items()}

                    results["camera_model"] = str(tags.get('Image Model', 'Yok'))
                    results["software"] = str(tags.get('Image Software', 'Yok'))
                    
                    # Tarih bilgileri
                    datetime_original = tags.get('EXIF DateTimeOriginal')
                    if datetime_original:
                        results["creation_date"] = str(datetime_original)
                    else: # Eğer DateTimeOriginal yoksa, DateTime kullan
                        datetime_val = tags.get('Image DateTime')
                        if datetime_val: results["creation_date"] = str(datetime_val)

                    # GPS verileri
                    gps_latitude = tags.get('GPS GPSLatitude')
                    gps_longitude = tags.get('GPS GPSLongitude')
                    
                    if gps_latitude and gps_longitude:
                        lat = self._convert_to_degrees(gps_latitude)
                        lon = self._convert_to_degrees(gps_longitude)
                        lat_ref = tags.get('GPS GPSLatitudeRef', "N")
                        lon_ref = tags.get('GPS GPSLongitudeRef', "E")

                        if str(lat_ref) == 'S': lat = -lat
                        if str(lon_ref) == 'W': lon = -lon

                        results["gps_coordinates"] = f"{lat}, {lon}"
                        try:
                            location = self.geolocator.reverse((lat, lon), timeout=5)
                            if location:
                                results["estimated_address"] = location.address
                            else:
                                results["estimated_address"] = "Adres bulunamadı."
                        except Exception as e:
                            results["estimated_address"] = f"Adres alınırken hata: {e}"

                # Manipülasyon tespiti (EXIF bütünlüğü)
                try:
                    piexif.load(file_path)
                except piexif.InvalidImageDataError:
                    results["manipulation_warnings"].append("EXIF verileri bozuk veya eksik. Olası manipülasyon.")
                
            except Exception as e:
                results["manipulation_warnings"].append(f"Resim EXIF analizi hatası: {e}")

        else: # Diğer dosya türleri (video, ses vb.) için mediainfo CLI kullan
            try:
                # mediainfo'yu JSON çıktısı verecek şekilde çalıştır
                command = ["mediainfo", "--Output=JSON", file_path]
                process = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10) # 10 saniye zaman aşımı
                mediainfo_output = json.loads(process.stdout)

                # mediainfo çıktısını raw_metadata'ya ekle
                results["raw_metadata"] = mediainfo_output

                # mediainfo çıktısından bazı temel bilgileri çekmeye çalış
                if "media" in mediainfo_output and "track" in mediainfo_output["media"]:
                    general_track = next((t for t in mediainfo_output["media"]["track"] if t["@type"] == "General"), None)
                    if general_track:
                        # Tarihleri mediainfo'dan alırken farklı isimler olabilir
                        results["creation_date"] = general_track.get('File_Creation_Date', general_track.get('Encoded_Date', 'Yok'))
                        results["modification_date"] = general_track.get('File_Modification_Date', 'Yok')
                        
                        # mediainfo'da 'camera_model' veya 'software' doğrudan bulunmayabilir,
                        # bunun yerine 'Writing_Application', 'Encoded_By', 'Encoded_Library_Name' gibi alanlar olabilir.
                        results["software"] = general_track.get('Writing_Application', general_track.get('Encoded_By', 'Yok'))
                        
                        # Kamera modeli için video track'lerine bakılabilir
                        video_track = next((t for t in mediainfo_output["media"]["track"] if t["@type"] == "Video"), None)
                        if video_track:
                            results["camera_model"] = video_track.get('Encoded_Library_Name', general_track.get('Manufacturer', 'Yok')) # Örnek

            except FileNotFoundError:
                results["manipulation_warnings"].append("MedyaInfo CLI aracı bulunamadı. Lütfen 'brew install mediainfo' ile yükleyin.")
            except subprocess.CalledProcessError as e:
                results["manipulation_warnings"].append(f"MedyaInfo çalıştırılırken hata: {e.cmd} - {e.stderr}")
            except subprocess.TimeoutExpired:
                results["manipulation_warnings"].append("MedyaInfo çalıştırılırken zaman aşımı yaşandı.")
            except json.JSONDecodeError:
                results["manipulation_warnings"].append("MedyaInfo çıktısı geçerli JSON değil. Çıktı hatası olabilir.")
            except Exception as e:
                results["manipulation_warnings"].append(f"Genel meta veri analizi hatası (MedyaInfo): {e}")

        # Dosya sistemi tarihleri (her zaman alınabilir, ancak meta veriden gelen daha güvenilirdir)
        try:
            # Sadece meta veriden tarih yoksa dosya sistemi tarihini kullan
            if results["creation_date"] == "Yok":
                results["creation_date"] = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            if results["modification_date"] == "Yok":
                results["modification_date"] = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass # Eğer alınamazsa "Yok" kalacak

        # Meta veri tarih tutarlılığı kontrolü (resimler için daha anlamlı, video için karmaşık)
        if file_extension in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
            if results["creation_date"] != "Yok" and results["raw_metadata"].get('EXIF DateTimeOriginal'):
                try:
                    exif_dt_str = str(results["raw_metadata"]['EXIF DateTimeOriginal'])
                    # EXIF formatı 'YYYY:MM:DD HH:MM:SS' olabilir
                    exif_dt = datetime.strptime(exif_dt_str.split(' ')[0], '%Y:%m:%d').date()
                    
                    file_dt_str = results["creation_date"].split(' ')[0]
                    file_dt = datetime.strptime(file_dt_str, '%Y-%m-%d').date()
                    
                    if exif_dt > file_dt: # EXIF tarihi dosya sistem tarihinden sonra ise şüpheli
                        results["manipulation_warnings"].append("EXIF çekim tarihi, dosya oluşturma tarihinden sonra. Olası manipülasyon.")
                    elif exif_dt != file_dt: # Tarihler tam olarak eşleşmiyorsa
                        results["manipulation_warnings"].append("EXIF çekim tarihi ile dosya oluşturma tarihi arasında farklılık var. İnceleyiniz.")
                except ValueError:
                    results["manipulation_warnings"].append("EXIF veya Dosya Sistemi tarihi formatı çözümlenemedi. Tarih tutarlılığı kontrolü yapılamadı.")

        # GUI güncellemesini ana thread'de yap
        self.main_app.after(0, lambda: self._update_gui_results(results))
        data_store.add_analysis_result(file_path, "metadata_analysis", results)
        self.main_app.status_bar.config(text=f"Meta Veri Modülü: '{os.path.basename(file_path)}' analizi tamamlandı.")

    def _convert_to_degrees(self, value):
        """EXIF formatındaki (derece, dakika, saniye) GPS değerlerini ondalık derecelere dönüştürür."""
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    def _clear_results(self):
        """GUI'deki tüm sonuçları temizler."""
        self.creation_date_label.config(text="Oluşturma Tarihi: Yok")
        self.modification_date_label.config(text="Değiştirme Tarihi: Yok")
        self.file_size_label.config(text="Dosya Boyutu: Yok")
        self.camera_model_label.config(text="Kamera Modeli: Yok")
        self.software_label.config(text="Yazılım: Yok")
        self.gps_coords_label.config(text="GPS Koordinatları: Yok")
        self.address_label.config(text="Tahmini Adres: Yok")
        self.manipulation_warning_label.config(text="Durum: Analiz bekleniyor.", foreground="yellow")
        self.meta_date_consistency_label.config(text="Meta Veri Tarih Tutarlılığı: Yok")
        self.exif_integrity_label.config(text="EXIF Bütünlüğü: Yok")
        self.all_metadata_text.config(state="normal")
        self.all_metadata_text.delete(1.0, tk.END)
        self.all_metadata_text.config(state="disabled")

    def _update_gui_results(self, results):
        """Analiz sonuçlarını GUI'ye yansıtır."""
        self.creation_date_label.config(text=f"Oluşturma Tarihi: {results['creation_date']}")
        self.modification_date_label.config(text=f"Değiştirme Tarihi: {results['modification_date']}")
        self.file_size_label.config(text=f"Dosya Boyutu: {results['file_size']}")
        self.camera_model_label.config(text=f"Kamera Modeli: {results['camera_model']}")
        self.software_label.config(text=f"Yazılım: {results['software']}")
        self.gps_coords_label.config(text=f"GPS Koordinatları: {results['gps_coordinates']}")
        self.address_label.config(text=f"Tahmini Adres: {results['estimated_address']}")

        if results["manipulation_warnings"]:
            self.manipulation_warning_label.config(text="!!! MANİPÜLASYON TESPİTİ Olası !!!\n" + "\n".join(results["manipulation_warnings"]), foreground="red")
        else:
            self.manipulation_warning_label.config(text="Durum: Manipülasyon tespiti yapılmadı.", foreground="green")

        # Tarih tutarlılığı ve EXIF bütünlüğü uyarılarını ayrı ayrı ele al
        date_consistency_warning = "EXIF çekim tarihi, dosya oluşturma tarihinden sonra. Olası manipülasyon."
        date_difference_warning = "EXIF çekim tarihi ile dosya oluşturma tarihi arasında farklılık var. İnceleyiniz."
        exif_corrupt_warning = "EXIF verileri bozuk veya eksik. Olası manipülasyon."

        if date_consistency_warning in results["manipulation_warnings"]:
            self.meta_date_consistency_label.config(text="Meta Veri Tarih Tutarlılığı: Şüpheli (EXIF > Dosya Sistemi)", foreground="red")
        elif date_difference_warning in results["manipulation_warnings"]:
            self.meta_date_consistency_label.config(text="Meta Veri Tarih Tutarlılığı: Farklılık var", foreground="orange")
        else:
            self.meta_date_consistency_label.config(text="Meta Veri Tarih Tutarlılığı: Tutarlı", foreground="green")

        if exif_corrupt_warning in results["manipulation_warnings"]:
            self.exif_integrity_label.config(text="EXIF Bütünlüğü: Bozuk/Eksik (Olası Manipülasyon)", foreground="red")
        else:
            self.exif_integrity_label.config(text="EXIF Bütünlüğü: Sağlam", foreground="green")


        self.all_metadata_text.config(state="normal")
        self.all_metadata_text.delete(1.0, tk.END)
        self.all_metadata_text.insert(tk.END, json.dumps(results["raw_metadata"], indent=2, ensure_ascii=False))
        self.all_metadata_text.config(state="disabled")

    def get_results(self):
        """Bu modülün kaydedilmiş sonuçlarını döndürür."""
        if self.main_app.current_analysis_file:
            return data_store.get_all_results_for_file(self.main_app.current_analysis_file).get("metadata_analysis")
        return None