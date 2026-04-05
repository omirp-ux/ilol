import json
import os


def get_pasta() -> str:
    """
    Retorna o diretório de dados do iLoL.
    - Android: solicita permissão em runtime e usa /sdcard/Android/data/com.ilol.ilol/files/
    - PC: pasta do próprio script (comportamento original).
    """
    try:
        from android.storage import primary_external_storage_path  # type: ignore
        from android.permissions import request_permissions, Permission, check_permission  # type: ignore

        # Solicita permissões de armazenamento em runtime
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])

        base  = primary_external_storage_path()
        pasta = os.path.join(base, "Android", "data", "com.ilol.ilol", "files")

        # Tenta criar a pasta — se ainda negar, usa fallback interno
        try:
            os.makedirs(pasta, exist_ok=True)
            return pasta
        except PermissionError:
            # Fallback: armazenamento interno do app (sempre acessível)
            from kivy.app import App  # type: ignore
            internal = App.get_running_app().user_data_dir
            os.makedirs(internal, exist_ok=True)
            return internal

    except ImportError:
        # Não é Android — retorna diretório do script (PC)
        return os.path.dirname(os.path.abspath(__file__))


# ─── Caminhos derivados ───────────────────────────────────────────────────────
PASTA       = get_pasta()
CONFIG_PATH = os.path.join(PASTA, "config.json")

# ─── Valores padrão ───────────────────────────────────────────────────────────
PADRAO = {
    "api_key":            "",
    "preco_core":         2000,
    "min_jogos_analista": 8,
    "min_jogos_comp":     3,
    "min_jogos_core":     2,
    "min_jogos_late":     2,
    "min_aparicoes_meta": 15,
    "ban_ids": [1001, 2003, 2010, 2052, 2055, 2138, 2139, 2140,
                2403, 3340, 3363, 3364, 222052],
    "modo_mayhem":        900,
    "region_americas":    "americas",
    "region_br":          "br1",
}

# ─── Funções públicas ─────────────────────────────────────────────────────────
def carregar() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in PADRAO.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    cfg = PADRAO.copy()
    salvar(cfg)
    return cfg


def salvar(cfg: dict) -> None:
    os.makedirs(PASTA, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
