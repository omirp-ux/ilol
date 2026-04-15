import os
import json
import platform

try:
    import migration

    _migration_module = migration
except ImportError:
    _migration_module = None
    try:
        import app_structure as app_struct
    except ImportError:
        app_struct = None


def get_pasta():
    if _migration_module is not None and hasattr(_migration_module, "data_dir"):
        return _migration_module.data_dir
    if app_struct is not None and hasattr(app_struct, "data_dir"):
        return app_struct.data_dir

    system = platform.system()
    if system == "Android":
        from android.storage import app_storage_path

        return app_storage_path()
    elif system == "Linux":
        return os.path.join(os.path.expanduser("~"), ".ilol")
    else:
        return os.path.join(os.path.expanduser("~"), "iLoL")


PASTA = get_pasta()
ARQUIVO_CONFIG = os.path.join(PASTA, "config.json")

PADRAO = {
    "api_key": "",
    "auto_up": True,
    "notificacoes": True,
    "tema": "dark",
    "idioma": "pt",
    "ban_ids": [],
    "preco_core": 2000,
    "min_jogos_analista": 8,
    "min_jogos_comp": 3,
    "min_jogos_core": 2,
    "min_jogos_late": 2,
    "min_aparicoes_meta": 15,
}


def carregar():
    if not os.path.exists(PASTA):
        os.makedirs(PASTA, exist_ok=True)
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return PADRAO.copy()
    return PADRAO.copy()


def salvar(config):
    if not os.path.exists(PASTA):
        os.makedirs(PASTA, exist_ok=True)
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False
