import json
import os

_pasta_cache = None


def get_pasta() -> str:
    """
    Retorna o diretório de dados do iLoL.

    - Android: usa context.getExternalFilesDir(None) via jnius.
      Isso retorna /storage/emulated/0/Android/data/com.ilol.ilol/files/
      e cria o diretório automaticamente, sem precisar de permissão
      explícita (o Android protege pelo package name, não por permission).
      jnius está disponível desde o início da Activity, antes do App Kivy.

    - PC: pasta do próprio script (comportamento original, sem mudança).
    """
    global _pasta_cache
    if _pasta_cache is not None:
        return _pasta_cache

    try:
        from jnius import autoclass  # type: ignore

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity

        # getExternalFilesDir(null) → Android/data/<package>/files/
        # O Android cria esse diretório automaticamente e garante acesso
        # ao próprio app sem nenhuma permissão de storage.
        external = context.getExternalFilesDir(None)
        if external is not None:
            path = external.getAbsolutePath()
        else:
            # Fallback: armazenamento interno do app (não visível no gerenciador)
            path = context.getFilesDir().getAbsolutePath()

        os.makedirs(path, exist_ok=True)
        _pasta_cache = path

    except ImportError:
        # Não é Android — usa diretório do script (PC)
        _pasta_cache = os.path.dirname(os.path.abspath(__file__))

    return _pasta_cache


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
    config_path = os.path.join(get_pasta(), "config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in PADRAO.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    cfg = PADRAO.copy()
    salvar(cfg)
    return cfg


def salvar(cfg: dict) -> None:
    pasta = get_pasta()
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def init_dados():
    import sys
    import shutil

    # Garante que a pasta existe (funciona em qualquer Android)
    pasta = get_pasta()
    try:
        os.makedirs(pasta, exist_ok=True)
    except Exception:
        pass

    # Verifica se a pasta realmente existe apos tentar criar
    if not os.path.exists(pasta):
        return  # Se nao conseguiu criar, retorna silenciosamente

    dados = ["itens.json", "Campeoes.json"]
    base_dir = (
        os.path.dirname(sys.modules["__main__"].__file__)
        if "__main__" in sys.modules
        else "."
    )

    for nome_arquivo in dados:
        dest = os.path.join(pasta, nome_arquivo)
        if not os.path.exists(dest):
            src = os.path.join(base_dir, nome_arquivo)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dest)
                except PermissionError:
                    shutil.copy(src, dest)
                except Exception:
                    pass

    hist_path = os.path.join(pasta, "historico_partidas.json")
    if not os.path.exists(hist_path):
        import json

        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump([], f)
