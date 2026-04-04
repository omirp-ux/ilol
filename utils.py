import re
import json
import os

def normalizar_champ(nome: str) -> str:
    """
    Normaliza nome de campeão para comparação segura.
    Remove espaços, apóstrofos, pontos e converte para lowercase.
    Exemplos:
        "Miss Fortune"  -> "missfortune"
        "MissFortune"   -> "missfortune"  (nome da Riot API)
        "Lee Sin"       -> "leesin"
        "Kha'Zix"       -> "khazix"
        "Dr. Mundo"     -> "drmundo"
    """
    return re.sub(r"[^a-z0-9]", "", nome.lower())

def carregar_display_names(pasta: str) -> dict:
    """
    Constrói mapa: nome_normalizado -> nome_de_exibição legível.
    Exemplo: {"missfortune": "Miss Fortune", "leesin": "Lee Sin", ...}
    """
    path = os.path.join(pasta, "campeoes.json")
    with open(path, encoding="utf-8") as f:
        champs = json.load(f)
    return {normalizar_champ(d["nome"]): d["nome"] for d in champs.values()}

def nome_exibicao(nome_api: str, display_map: dict) -> str:
    """Converte nome da Riot API para nome legível usando o mapa."""
    return display_map.get(normalizar_champ(nome_api), nome_api)

def contar_partidas(pasta: str) -> int:
    """Retorna o número de partidas no banco de dados."""
    path = os.path.join(pasta, "historico_partidas.json")
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            return len(json.load(f))
    except Exception:
        return -1  # -1 indica arquivo corrompido
