import pkgutil, pkg_resources

def load_text_file(path):
    data = pkgutil.get_data(__name__, path)
    if data is None:
        raise FileNotFoundError(f'{path!r} not found in {__name__}.')
    return data.decode()

def resource_listdir(path):
    return [f for f in pkg_resources.resource_listdir(__name__, path) if f != '']
