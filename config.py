import os
import json

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

# Android: usa pasta app-scoped (Android/data/) - acessível
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        context = PythonActivity.mActivity
        external = context.getExternalFilesDir(None)
        if external is not None:
            return str(external)  # Path real usado pelo sistema
    except Exception:
        pass

    # Desktop/Android fallback
    return os.path.expanduser("~/iLoL")


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
        try:
            os.makedirs(PASTA, exist_ok=True)
        except PermissionError:
            # Sem permissão - retorna config padrão sem salvar
            return PADRAO.copy()
        except Exception:
            return PADRAO.copy()
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, PermissionError):
            pass
    config = PADRAO.copy()
    salvar(config)
    return config


def salvar(config):
    if not os.path.exists(PASTA):
        try:
            os.makedirs(PASTA, exist_ok=True)
        except PermissionError:
            return False
        except Exception:
            return False
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except (IOError, PermissionError):
        return False


def init_dados():
    import sys
    import shutil

    # Garante que a pasta existe (funciona em qualquer Android)
    try:
        os.makedirs(PASTA, exist_ok=True)
    except Exception:
        pass

    # Verifica se a pasta realmente existe apos tentar criar
    if not os.path.exists(PASTA):
        return  # Se nao conseguiu criar, retorna silenciosamente

    dados = ["itens.json", "Campeoes.json"]
    base_dir = (
        os.path.dirname(sys.modules["__main__"].__file__)
        if "__main__" in sys.modules
        else "."
    )

    for nome_arquivo in dados:
        dest = os.path.join(PASTA, nome_arquivo)
        if not os.path.exists(dest):
            src = os.path.join(base_dir, nome_arquivo)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dest)
                except PermissionError:
                    shutil.copy(src, dest)
                except Exception:
                    pass

    hist_path = os.path.join(PASTA, "historico_partidas.json")
    if not os.path.exists(hist_path):
        import json

        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump([], f)
