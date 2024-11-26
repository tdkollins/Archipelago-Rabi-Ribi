"""
Utility used across the apworld
"""
import pkgutil

rabi_ribi_base_id: int = 8350438193300

def get_rabi_ribi_base_id() -> int:
    return rabi_ribi_base_id

def load_text_file(path):
    return pkgutil.get_data(__name__, path).decode()
