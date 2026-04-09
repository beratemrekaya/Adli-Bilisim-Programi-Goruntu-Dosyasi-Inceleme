import json
import os

class DataStore:
    """
    Analiz sonuçlarını JSON formatında saklamak için basit bir veri depolama sınıfı.
    """
    def __init__(self, db_file="forensics_data.json"):
        self.db_file = db_file
        self.data = self._load_data()

    def _load_data(self):
        """Veritabanı dosyasını yükler."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"'{self.db_file}' dosyası bozuk. Yeni bir veritabanı oluşturuluyor.")
                    return {}
        return {}

    def _save_data(self):
        """Veritabanı dosyasını kaydeder."""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_analysis_result(self, file_path, module_name, result):
        """Belirli bir dosya ve modül için analiz sonucunu ekler."""
        file_key = os.path.abspath(file_path) # Dosya yolunu benzersiz anahtar olarak kullan
        if file_key not in self.data:
            self.data[file_key] = {"filename": os.path.basename(file_path), "analyses": {}}
        
        self.data[file_key]["analyses"][module_name] = result
        self._save_data()
        print(f"Analiz sonucu kaydedildi: {os.path.basename(file_path)} - {module_name}")

    def get_analysis_result(self, file_path, module_name):
        """Belirli bir dosya ve modül için analiz sonucunu döndürür."""
        file_key = os.path.abspath(file_path)
        return self.data.get(file_key, {}).get("analyses", {}).get(module_name)

    def get_all_results_for_file(self, file_path):
        """Belirli bir dosya için tüm analiz sonuçlarını döndürür."""
        file_key = os.path.abspath(file_path)
        return self.data.get(file_key, {}).get("analyses", {})

    def get_all_files(self):
        """Depodaki tüm dosyaların yollarını döndürür."""
        return list(self.data.keys())

# Global veritabanı objesi (veya ForensicAnalysisTool içinde başlatılabilir)
data_store = DataStore()