"""
Utility used across the apworld
"""
import pkgutil

def load_text_file(path):
    return pkgutil.get_data(__name__, path).decode()
