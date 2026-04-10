# 🔍 Kaya Forensics

[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/beratemrekaya/Forensic-Analysis-Tool?style=social)](https://github.com/beratemrekaya/Forensic-Analysis-Tool/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/beratemrekaya/Forensic-Analysis-Tool?style=social)](https://github.com/beratemrekaya/Forensic-Analysis-Tool/network/members)

<p align="center">
  <img src="https://raw.githubusercontent.com/beratemrekaya/Adli-Bilisim-Programi-Goruntu-Dosyasi-nceleme/refs/heads/main/app.png" alt="Adli Bilişim Başlık Görseli">
  <br>
  <em>Dijital delillerin derinlemesine analizi için kapsamlı bir çözüm.</em>
</p>

## 🌟 Projeye Genel Bakış

Adli Bilişim yazılımı Kaya Forensics, çeşitli dijital deliller üzerinde kapsamlı analizler yapabilen, kullanıcı dostu bir masaüstü uygulamasıdır. Özellikle görüntü dosyaları ve genel dosya sistemleri üzerinde meta veri analizi, görüntü bütünlüğü kontrolü, kamera adliyesi ve dosya kurtarma gibi kritik adli bilişim görevlerini otomatize etmeyi hedefler. Kullanıcıların delil yönetimi, detaylı raporlama ve olay zinciri oluşturma süreçlerini kolaylaştırır.

Bu Kaya Forensics, adli araştırmacılara, siber güvenlik uzmanlarına ve dijital delillerle çalışan herkese zaman kazandıran ve verimli bir çalışma ortamı sunar.

## ✨ Özellikler

*   **Meta Veri Analizi:** Görüntü dosyalarından (JPG, PNG, TIFF vb.) EXIF verilerini, oluşturulma/değiştirilme tarihlerini ve GPS koordinatları gibi kritik bilgileri çıkarır.
*   **Görüntü Bütünlüğü Kontrolü (ELA):** Hata Seviyesi Analizi (Error Level Analysis - ELA) ile görüntü manipülasyonu izlerini tespit eder.
*   **Kamera Adliyesi:** Kamera üreticisi, modeli, yazılımı, pozlama süresi ve ISO gibi kamera spesifik verileri inceleyerek kaynağı hakkında bilgi edinir. (PRNU analizi geliştirme aşamasındadır.)
*   **Dosya Kurtarma:** Silinmiş veya kaybolmuş dosyaları kurtarmak için temel yetenekler sunar.
*   **Olay Zinciri Oluşturma:** Analiz edilen deliller arasındaki ilişkileri ve kronolojik olay akışını görselleştirmeye yardımcı olur (geliştirme aşamasında).
*   **Kullanıcı Dostu Arayüz:** Tkinter ile geliştirilmiş sezgisel ve modern bir grafik arayüz (GUI).
*   **Detaylı Raporlama:** Analiz sonuçlarını HTML formatında özetleyen kapsamlı raporlar oluşturur.

## 🚀 Kurulum

Projeyi yerel makinenizde kurmak ve çalıştırmak için aşağıdaki adımları izleyin.

### Ön Gereksinimler

*   Python 3.x (Önerilen: Python 3.8+)
*   `pip` (Python paket yöneticisi)

### Adımlar

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/beratemrekaya/Forensic-Analysis-Tool.git
    cd Forensic-Analysis-Tool
    ```
2.  **Sanal Ortam Oluşturun (Önerilir):**
    ```bash
    python -m venv venv
    ```
3.  **Sanal Ortamı Aktive Edin:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  **Gerekli Paketleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *Not: `requirements.txt` dosyasını kendiniz oluşturmanız gerekecektir. Aşağıdaki "Bağımlılıklar" bölümüne bakın.*

5.  **Uygulamayı Çalıştırın:**
    ```bash
    python main.py
    ```

## 📋 Bağımlılıklar

Gerekli Python paketlerini `requirements.txt` dosyasına ekleyin. Bu dosyayı projenizin kök dizininde oluşturun:

Pillow
exifread
scikit-image # Eğer ImageIntegrityModule'de kullanılıyorsa
numpy # Eğer ImageIntegrityModule veya diğerlerinde kullanılıyorsa
folium # Eğer EventChainModule'de harita oluşturuluyorsa

`requirements.txt` dosyanızı oluşturduktan sonra `pip install -r requirements.txt` komutuyla tüm bağımlılıkları kolayca kurabilirsiniz.

## 📂 Dizin Yapısı

Projenin anlaşılır ve düzenli bir yapısı vardır:

forensic_analysis_tool/
├── main.py # Ana uygulama dosyası
├── modules/ # Çeşitli analiz modülleri
│ ├── metadata_analysis_module.py
│ ├── image_integrity_module.py
│ ├── event_chain_module.py
│ ├── camera_forensics_module.py
│ └── file_recovery_module.py
├── utils/ # Yardımcı fonksiyonlar ve sınıflar
│ ├── gui_elements.py
│ ├── file_operations.py
│ └── data_storage.py
├── reports/ # Raporlama ile ilgili dosyalar
│ ├── report_generator.py
│ └── report_templates/ # Rapor şablonları (örn. HTML)
├── assets/ # Statik varlıklar (örn. ikonlar)
│ └── images/ # Başlık görseli gibi ek görseller
├── recovered_files/ # Kurtarılan dosyaların depolandığı dizin
└── requirements.txt # Python bağımlılıkları listesi

qTox contact: 18EAB3D22CD3B9773AF7FBF51E818C8DA779048DF561B497FE944D6E1B92097883DBA8B805E3
