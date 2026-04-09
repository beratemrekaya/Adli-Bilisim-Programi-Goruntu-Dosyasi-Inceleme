import os
import shutil

def ensure_directory_exists(path):
    """Belirtilen dizinin varlığını kontrol eder, yoksa oluşturur."""
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def get_file_extension(filepath):
    """Bir dosya yolunun uzantısını döndürür."""
    return os.path.splitext(filepath)[1].lower()

def get_filename_without_extension(filepath):
    """Bir dosya yolunun dosya adını uzantısız döndürür."""
    return os.path.splitext(os.path.basename(filepath))[0]

def copy_file(source_path, destination_dir):
    """Bir dosyayı belirli bir dizine kopyalar."""
    ensure_directory_exists(destination_dir)
    shutil.copy(source_path, destination_dir)
    return os.path.join(destination_dir, os.path.basename(source_path))

def read_text_file(filepath):
    """Bir metin dosyasının içeriğini okur."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Metin dosyası okunurken hata oluştu '{filepath}': {e}")
        return None

def write_text_file(filepath, content):
    """Bir metin içeriğini dosyaya yazar."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Metin dosyasına yazılırken hata oluştu '{filepath}': {e}")
        return False