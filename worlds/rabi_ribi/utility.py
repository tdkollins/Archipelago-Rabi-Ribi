"""
Utility used across the apworld
"""
import os
import pkgutil

def get_world_directory():
    """
    Get the base rabi_ribi world directory
    """
    return os.path.dirname(os.path.abspath(__file__))

def load_text_file(path):
    return pkgutil.get_data(__name__, path).decode()
