"""
Utility used across the apworld
"""
import pkgutil, pkg_resources

rabi_ribi_base_id: int = 8350438193300

def get_rabi_ribi_base_id() -> int:
    return rabi_ribi_base_id

def load_text_file(path):
    data = pkgutil.get_data(__name__, path)
    if data is None:
        raise FileNotFoundError(f'{path!r} not found in {__name__}.')
    return data.decode()

def resource_listdir(path):
    return [f for f in pkg_resources.resource_listdir(__name__, path) if f != '']
