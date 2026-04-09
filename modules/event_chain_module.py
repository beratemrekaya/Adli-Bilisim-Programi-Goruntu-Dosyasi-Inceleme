import tkinter as tk
from tkinter import ttk, messagebox
import os
import folium
import json
import webbrowser
from datetime import datetime
from collections import defaultdict
import threading
from utils.data_storage import data_store

class EventChainModule:
    def __init__(self, parent_frame, main_app):
        self.parent_frame = parent_frame
        self.main_app = main_app
        self._create_widgets()
        self.map_file_path = "event_chain_map.html"

    def _create_widgets(self):
        ttk.Label(self.parent_frame, text="Olay Zinciri Oluşturma ve Konumsal Haritalama", font=("Arial", 14, "bold"), background="#2b2b2b", foreground="white").pack(pady=10)

        event_chain_frame = ttk.LabelFrame(self.parent_frame, text="Kronolojik Olay Akışı", padding=10, style='TFrame')
        event_chain_frame.pack(fill="x", padx=10, pady=5, expand=True)
        self.event_chain_text = tk.Text(event_chain_frame, wrap="word", height=15, bg="#4a4a4a", fg="white", bd=0, relief="flat")
        self.event_chain_text.pack(fill="both", expand=True)
        self.event_chain_text.config(state="disabled")

        map_frame = ttk.LabelFrame(self.parent_frame, text="Olay Konum Haritası", padding=10, style='TFrame')
        map_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(map_frame, text="Oluşturulan haritayı tarayıcınızda açmak için butona tıklayın.", background="#2b2b2b", foreground="white").pack(anchor="w")
        self.open_map_button = tk.Button(map_frame, text="Haritayı Aç", command=self._open_map, bg="#007bff", fg="white", state="disabled")
        self.open_map_button.pack(pady=5, anchor="w")
        self.map_status_label = ttk.Label(map_frame, text="Durum: Harita oluşturulmadı.", background="#2b2b2b", foreground="white", wraplength=500)
        self.map_status_label.pack(anchor="w")

        analyze_all_button = tk.Button(self.parent_frame, text="Tüm Deliller Üzerinde Olay Zinciri Analizi Yap", command=self._run_full_analysis, bg="#d9534f", fg="white", font=("Arial", 10, "bold"))
        analyze_all_button.pack(pady=10)

    def _run_full_analysis(self):
        self.main_app.status_bar.config(text="Olay Zinciri Modülü: Tüm deliller üzerinde analiz başlatılıyor...")
        self._clear_results()
        
        threading.Thread(target=self._analyze_all_evidence_in_thread).start()

    def _analyze_all_evidence_in_thread(self):
        all_files = data_store.get_all_files()
        
        event_data = []

        for file_path in all_files:
            meta_results = data_store.get_analysis_result(file_path, "metadata_analysis")

            file_creation_date = None
            if meta_results and meta_results["creation_date"] != "Yok":
                try:
                    file_creation_date = datetime.strptime(meta_results["creation_date"], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        file_creation_date = datetime.strptime(meta_results["creation_date"].split(' ')[0], '%Y:%m:%d')
                    except ValueError:
                        pass
            
            event_entry = {
                "file": os.path.basename(file_path),
                "timestamp": file_creation_date,
                "location": None,
            }

            if meta_results and meta_results["gps_coordinates"] != "Yok":
                try:
                    lat, lon = map(float, meta_results["gps_coordinates"].split(', '))
                    event_entry["location"] = (lat, lon)
                except ValueError:
                    pass
            
            event_data.append(event_entry)
        
        event_data.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min)

        event_chain_output = ""
        for event in event_data:
            ts_str = event["timestamp"].strftime('%Y-%m-%d %H:%M:%S') if event["timestamp"] else "Tarih Yok"
            loc_str = f"Konum: {event['location'][0]:.4f}, {event['location'][1]:.4f}" if event["location"] else "Konum Yok"
            event_chain_output += f"[{ts_str}] - Dosya: {event['file']} | {loc_str}\n"
        
        map_created_successfully = self._create_folium_map(event_data)

        results = {
            "event_chain_text": event_chain_output,
            "map_created": map_created_successfully,
            "map_file_path": self.map_file_path if map_created_successfully else None,
        }

        self.main_app.after(0, lambda: self._update_gui_results(results))
        data_store.add_analysis_result("all_evidence", "event_chain_analysis", results)
        self.main_app.status_bar.config(text="Olay Zinciri Modülü: Tüm deliller üzerinde analiz tamamlandı.")

    def _create_folium_map(self, event_data):
        try:
            initial_location = [0, 0]
            valid_locations = [e["location"] for e in event_data if e["location"]]
            if valid_locations:
                initial_location = [sum(c[0] for c in valid_locations) / len(valid_locations),
                                    sum(c[1] for c in valid_locations) / len(valid_locations)]
            else:
                initial_location = [39.9334, 32.8597]

            fmap = folium.Map(location=initial_location, zoom_start=10)

            for event in event_data:
                if event["location"]:
                    popup_text = f"<b>Dosya:</b> {event['file']}<br>"
                    popup_text += f"<b>Tarih:</b> {event['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if event['timestamp'] else 'Yok'}<br>"
                    
                    folium.Marker(
                        location=event["location"],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(fmap)
            
            fmap.save(self.map_file_path)
            return True
        except Exception as e:
            self.main_app.status_bar.config(text=f"Olay Zinciri Modülü: Harita oluşturulurken hata: {e}", fg="red")
            return False

    def _open_map(self):
        if os.path.exists(self.map_file_path):
            webbrowser.open(f"file:///{os.path.abspath(self.map_file_path)}")
        else:
            messagebox.showerror("Hata", "Harita dosyası bulunamadı. Lütfen önce analiz yapın.")

    def _clear_results(self):
        self.event_chain_text.config(state="normal")
        self.event_chain_text.delete(1.0, tk.END)
        self.event_chain_text.config(state="disabled")
        self.open_map_button.config(state="disabled")
        self.map_status_label.config(text="Durum: Harita oluşturulmadı.", foreground="white")

    def _update_gui_results(self, results):
        self.event_chain_text.config(state="normal")
        self.event_chain_text.delete(1.0, tk.END)
        self.event_chain_text.insert(tk.END, results["event_chain_text"])
        self.event_chain_text.config(state="disabled")

        if results["map_created"]:
            self.open_map_button.config(state="normal")
            self.map_status_label.config(text=f"Harita oluşturuldu: {os.path.basename(results['map_file_path'])}", foreground="green")
        else:
            self.open_map_button.config(state="disabled")
            self.map_status_label.config(text="Harita oluşturulamadı.", foreground="red")
        
        self.main_app.status_bar.config(text="Olay Zinciri Modülü: Analiz sonuçları güncellendi.")

    def get_results(self):
        return data_store.get_analysis_result("all_evidence", "event_chain_analysis")