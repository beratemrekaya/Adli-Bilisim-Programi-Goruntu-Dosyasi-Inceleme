import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk # PIL'e hala ihtiyaç olabilir, yorum olarak bıraktım.
import os
import threading
from datetime import datetime

# --- Modülleri İçe Aktar ---
# Bu modüllerin yan dizinde veya PATH'te olduğundan emin olun
from modules.metadata_analysis_module import MetadataAnalysisModule
from modules.image_integrity_module import ImageIntegrityModule
from modules.event_chain_module import EventChainModule
from modules.camera_forensics_module import CameraForensicsModule
from modules.file_recovery_module import FileRecoveryModule

# --- Utility Modüller ---
from utils.gui_elements import ScrollableFrame, create_tooltip
from utils.file_operations import ensure_directory_exists
from utils.data_storage import data_store
from reports.report_generator import ReportGenerator

class ForensicAnalysisTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kaya Forensics")
        self.geometry("1400x900")
        self.configure(bg="#2b2b2b")

        self.current_analysis_file = None
        self.evidence_files = []

        # Gerekli dizinlerin varlığını kontrol et ve oluştur
        ensure_directory_exists("assets/icons") # İkonlar kullanılmayacak olsa da dizin yapısını korumak için
        ensure_directory_exists("reports/report_templates")
        ensure_directory_exists("recovered_files")

        self._load_assets() # İkonlar kullanılmasa da metod çağrısı kaldı
        self._create_widgets()
        self._load_modules()

        self.report_generator = ReportGenerator()

        self.status_bar.config(text="Sistem Hazır. Delil eklemek için 'Delil Ekle' butonuna tıklayın.")

    def _load_assets(self):
        # İkonlar kullanılmayacağı için bu metod boş bırakıldı veya referanslar None olarak ayarlandı.
        # Bu sayede ikon dosyası bulunamadı uyarısı alınmayacaktır.
        self.icon_add_file = None
        self.icon_report = None
        self.icon_warning = None
        self.icon_info = None

    def _create_widgets(self):
        s = ttk.Style()
        s.theme_use('default')
        s.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        s.configure('TNotebook.Tab', background='#4a4a4a', foreground='white', padding=[10, 5])
        s.map('TNotebook.Tab', background=[('selected', '#007acc')], foreground=[('selected', 'white')])
        s.configure('TFrame', background='#2b2b2b')
        s.configure('TLabelFrame', background='#2b2b2b', foreground='white')
        s.configure('TLabelFrame.Label', background='#2b2b2b', foreground='white')
        s.configure('Vertical.TScrollbar', background='#555555', troughcolor='#3c3c3c')
        s.configure('Horizontal.TScrollbar', background='#555555', troughcolor='#3c3c3c')

        self.left_panel = tk.Frame(self, width=280, bg="#3c3c3c", relief="raised", bd=1)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)
        self.left_panel.pack_propagate(False)

        tk.Label(self.left_panel, text="Delil Yönetimi", bg="#3c3c3c", fg="white", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Delil Ekle butonu: Arka plan koyu gri, yazı beyaz, ikon kaldırıldı
        add_evidence_button = tk.Button(self.left_panel, text="Delil Ekle", command=self._add_evidence, 
                                        bg="#4a4a4a", fg="white", # Arka plan rengi ve yazı rengi ayarlandı
                                        font=("Arial", 10, "bold"), relief="raised") # image parametresi kaldırıldı
        add_evidence_button.pack(pady=5, padx=10, fill="x")
        create_tooltip(add_evidence_button, "Analiz edilecek dosya(ları) ekleyin.")

        tk.Label(self.left_panel, text="Delil Listesi", bg="#3c3c3c", fg="white", font=("Arial", 10)).pack(pady=5)
        self.evidence_listbox = tk.Listbox(self.left_panel, bg="#4a4a4a", fg="white", selectbackground="#007acc", relief="flat", bd=0)
        self.evidence_listbox.pack(padx=10, fill="both", expand=True)
        self.evidence_listbox.bind("<<ListboxSelect>>", self._on_evidence_select)

        self.analysis_panel = ttk.Notebook(self)
        self.analysis_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.metadata_frame = ttk.Frame(self.analysis_panel)
        self.analysis_panel.add(self.metadata_frame, text="Meta Veri Analizi")
        
        self.integrity_frame = ttk.Frame(self.analysis_panel)
        self.analysis_panel.add(self.integrity_frame, text="Görüntü Bütünlüğü")

        self.camera_forensics_frame = ttk.Frame(self.analysis_panel)
        self.analysis_panel.add(self.camera_forensics_frame, text="Kamera Adliyesi")
        
        self.file_recovery_frame = ttk.Frame(self.analysis_panel)
        self.analysis_panel.add(self.file_recovery_frame, text="Dosya Kurtarma")
        
        self.event_chain_frame = ttk.Frame(self.analysis_panel)
        self.analysis_panel.add(self.event_chain_frame, text="Olay Zinciri")

        self.status_bar = tk.Label(self, text="Sistem Hazır.", bd=1, relief="sunken", anchor="w", bg="#3c3c3c", fg="white")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Rapor Oluştur butonu: Arka plan koyu gri, yazı beyaz, ikon kaldırıldı
        report_button = tk.Button(self.status_bar, text="Rapor Oluştur", command=self._generate_report, 
                                  bg="#4a4a4a", fg="white", # Arka plan rengi ve yazı rengi ayarlandı
                                  font=("Arial", 9, "bold")) # image parametresi kaldırıldı
        report_button.pack(side="right", padx=5, pady=2)

    def _load_modules(self):
        self.metadata_module = MetadataAnalysisModule(self.metadata_frame, self)
        self.integrity_module = ImageIntegrityModule(self.integrity_frame, self)
        self.camera_forensics_module = CameraForensicsModule(self.camera_forensics_frame, self)
        self.file_recovery_module = FileRecoveryModule(self.file_recovery_frame, self)
        self.event_chain_module = EventChainModule(self.event_chain_frame, self)

    def _add_evidence(self):
        file_paths = filedialog.askopenfilenames(
            title="Analiz Edilecek Delilleri Seçin",
            filetypes=[("Tüm Desteklenen Dosyalar", "*.jpg *.jpeg *.png *.tif *.tiff"),
                       ("Resim Dosyaları", "*.jpg *.jpeg *.png *.tif *.tiff"),
                       ("Tüm Dosyalar", "*.*")]
        )
        if file_paths:
            for fp in file_paths:
                if fp not in self.evidence_files:
                    self.evidence_files.append(fp)
                    self.evidence_listbox.insert(tk.END, os.path.basename(fp))
            self.status_bar.config(text=f"{len(file_paths)} yeni delil eklendi. Toplam {len(self.evidence_files)} delil var.")

    def _on_evidence_select(self, event):
        selected_indices = self.evidence_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_filename = self.evidence_listbox.get(index)
            self.current_analysis_file = next((f for f in self.evidence_files if os.path.basename(f) == selected_filename), None)
            
            if self.current_analysis_file:
                self.status_bar.config(text=f"Analiz Ediliyor: {os.path.basename(self.current_analysis_file)}")
                self.run_all_analyses_for_file(self.current_analysis_file)
            else:
                self.status_bar.config(text="Hata: Seçilen dosya yolu bulunamadı.", fg="red")

    def run_all_analyses_for_file(self, file_path):
        threading.Thread(target=self._run_analyses_in_thread, args=(file_path,)).start()

    def _run_analyses_in_thread(self, file_path):
        self.status_bar.config(text=f"Analiz Başladı: {os.path.basename(file_path)}...")
        
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
            self.metadata_module.analyze(file_path)
            self.integrity_module.analyze(file_path)
            self.camera_forensics_module.analyze(file_path)
        else:
            self.status_bar.config(text=f"Desteklenmeyen dosya türü: {file_extension}", fg="red")
            messagebox.showerror("Desteklenmeyen Dosya", f"'{file_extension}' uzantılı dosyalar için tam analiz desteklenmiyor.")
            return

        self.status_bar.config(text=f"Analiz Tamamlandı: {os.path.basename(file_path)}.")
        messagebox.showinfo("Analiz Tamamlandı", f"'{os.path.basename(file_path)}' için tüm analizler tamamlandı.")

    def _generate_report(self):
        report_data = {
            "file_path": self.current_analysis_file if self.current_analysis_file else "Tüm Delillerin Özeti",
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metadata_results": self.metadata_module.get_results(),
            "integrity_results": self.integrity_module.get_results(),
            "camera_forensics_results": self.camera_forensics_module.get_results(),
            "event_chain_results": self.event_chain_module.get_results(),
        }
        
        report_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Rapor", "*.html")],
            title="Rapor Kaydet",
            initialfile=f"Adli_Analiz_Raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if report_path:
            try:
                self.report_generator.generate_html_report(report_data, report_path)
                self.status_bar.config(text=f"Rapor oluşturuldu: {os.path.basename(report_path)}")
                messagebox.showinfo("Rapor Oluşturuldu", f"Analiz raporu '{os.path.basename(report_path)}' konumuna kaydedildi.")
            except Exception as e:
                messagebox.showerror("Rapor Hatası", f"Rapor oluşturulurken bir hata oluştu: {e}")
                self.status_bar.config(text=f"Rapor oluşturma hatası: {e}", fg="red")

if __name__ == "__main__":
    app = ForensicAnalysisTool()
    app.mainloop()