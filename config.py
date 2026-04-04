import json
import os


def get_pasta() -> str:
    """
    Retorna o diretório de dados do iLoL.

    - Android: /sdcard/Android/data/com.ilol.app/files/
      Acessível sem root via gerenciador de arquivos, cabo USB, etc.
    - PC: pasta do próprio script (comportamento original, sem mudança).
    """
    try:
        from android.storage import primary_external_storage_path  # type: ignore
        base  = primary_external_storage_path()
        pasta = os.path.join(base, "Android", "data", "com.ilol.app", "files")
        os.makedirs(pasta, exist_ok=True)
        return pasta
    except ImportError:
        # Não é Android — retorna o diretório do script (comportamento original)
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
    """Lê config.json, preenchendo chaves faltantes com os valores padrão."""
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
    """Persiste o dicionário de configuração em config.json."""
    os.makedirs(PASTA, exist_ok=True)          # garante que a pasta existe
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)