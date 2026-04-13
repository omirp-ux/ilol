import requests
import time
import json
import os
import random
import threading

import config as cfg_mod

from config import get_pasta
PASTA = get_pasta()

class MineradorPuroAram:
    def __init__(self, api_key: str, log_func=print):
        self.api_key = api_key
        self.log = log_func

        self.arquivo_historico = os.path.join(PASTA, "historico_partidas.json")
        self.arquivo_champs    = os.path.join(PASTA, "campeoes.json")
        self.arquivo_fila      = os.path.join(PASTA, "fila_puuids.json")
        self.arquivo_visitados = os.path.join(PASTA, "visitados.json")

        with open(self.arquivo_champs, "r", encoding="utf-8") as f:
            self.tradutor_champs = {int(k): v for k, v in json.load(f).items()}

        # Carrega fila e visitados persistidos
        self.fila_exploracao = self._carregar_json(self.arquivo_fila, [])
        visitados_lista      = self._carregar_json(self.arquivo_visitados, [])
        self.visitados       = set(visitados_lista)

        self._contador_saves = 0

    def _carregar_json(self, path, padrao):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return padrao
        return padrao

    def _salvar_fila_e_visitados(self):
        with open(self.arquivo_fila, "w", encoding="utf-8") as f:
            json.dump(self.fila_exploracao[:500], f)
        with open(self.arquivo_visitados, "w", encoding="utf-8") as f:
            json.dump(list(self.visitados)[-2000:], f)

    def _get(self, url: str, tentativas=3):
        cfg = cfg_mod.carregar()
        region_americas = cfg.get("region_americas", "americas")
        for t in range(tentativas):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    return r.json()
                elif r.status_code == 429:
                    wait = int(r.headers.get("Retry-After", 30))
                    self.log(f"[Rate Limit] Aguardando {wait}s...\n")
                    time.sleep(wait)
                elif r.status_code == 403:
                    self.log("[ERRO 403] API Key expirada ou invalida! Atualize em Configuracoes.\n")
                    return None
                elif r.status_code == 404:
                    return None
                else:
                    self.log(f"[HTTP {r.status_code}] {url[:60]}\n")
                    time.sleep(2)
            except requests.RequestException as e:
                self.log(f"[Conexao] {e}\n")
                time.sleep(3)
        return None

    def buscar_sementes(self) -> list:
        self.log("Buscando sementes via partidas existentes...\n")
        base = self._carregar_json(self.arquivo_historico, [])
        if not base:
            return []

        amostra = random.sample(base, min(len(base), 5))
        puuids = []
        for p in amostra:
            m_id = p.get("match_id")
            if not m_id:
                continue
            cfg = cfg_mod.carregar()
            url = (f"https://{cfg['region_americas']}.api.riotgames.com"
                   f"/lol/match/v5/matches/{m_id}?api_key={self.api_key}")
            dados = self._get(url)
            if dados:
                for part in dados.get("info", {}).get("participants", []):
                    puuids.append(part["puuid"])
            time.sleep(1.2)
        return puuids

    def minerar_jogador(self, puuid: str):
        cfg = cfg_mod.carregar()
        modo_mayhem = cfg.get("modo_mayhem", 900)

        url_ids = (f"https://{cfg['region_americas']}.api.riotgames.com"
                   f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
                   f"?start=0&count=100&api_key={self.api_key}")
        match_ids = self._get(url_ids)
        if not match_ids:
            return

        base = self._carregar_json(self.arquivo_historico, [])
        ids_existentes = {p["match_id"] for p in base}
        novos = 0

        self.log(f"Varrendo {len(match_ids)} partidas... (banco: {len(base):,})\n")

        for m_id in match_ids:
            if m_id in ids_existentes:
                continue

            url_d = (f"https://{cfg['region_americas']}.api.riotgames.com"
                     f"/lol/match/v5/matches/{m_id}?api_key={self.api_key}")
            dados = self._get(url_d)
            if not dados:
                time.sleep(1.2)
                continue

            info = dados.get("info", {})
            modo = info.get("queueId")
            game_mode = info.get("gameMode", "")

            if modo == modo_mayhem or game_mode == "ARAM":
                participantes = info.get("participants", [])

                for part in participantes:
                    p_id = part.get("puuid")
                    if p_id and p_id not in self.visitados and p_id not in self.fila_exploracao:
                        self.fila_exploracao.append(p_id)

                for p in participantes:
                    meu_time = p.get("teamId")
                    tags_inimigas = []
                    for inimigo in participantes:
                        if inimigo.get("teamId") != meu_time:
                            tid = inimigo.get("championId")
                            tags_inimigas.extend(
                                self.tradutor_champs.get(tid, {}).get("tags", [])
                            )

                    base.append({
                        "match_id": m_id,
                        "meu_campeao": p.get("championName", ""),
                        "vitoria": p.get("win", False),
                        "itens": [
                            p.get(f"item{i}")
                            for i in range(7)
                            if p.get(f"item{i}", 0) != 0
                        ],
                        "comp_inimiga_tags": tags_inimigas,
                    })

                novos += len(participantes)
                self.log(f"+{len(participantes)} registros | {m_id}\n")

                with open(self.arquivo_historico, "w", encoding="utf-8") as f:
                    json.dump(base, f, indent=4, ensure_ascii=False)

            time.sleep(1.2)

        self._contador_saves += 1
        if self._contador_saves % 5 == 0:
            self._salvar_fila_e_visitados()


def run_miner_loop(stop_event: threading.Event, pause_event: threading.Event, log_func=print):
    """
    Loop principal do minerador, controlado por threading.Events.
    Chamado pela GUI em uma thread separada.
    """
    cfg = cfg_mod.carregar()
    api_key = cfg.get("api_key", "")

    if not api_key:
        log_func("[ERRO] API Key nao configurada. Acesse a aba Configuracoes.\n")
        return

    miner = MineradorPuroAram(api_key=api_key, log_func=log_func)
    log_func("=== MINERADOR ARAM v5.0 INICIADO ===\n")

    while not stop_event.is_set():
        if pause_event.is_set():
            time.sleep(0.5)
            continue

        if len(miner.fila_exploracao) > 1000:
            miner.fila_exploracao = random.sample(miner.fila_exploracao, 500)

        if not miner.fila_exploracao:
            log_func("Fila vazia. Buscando novas sementes...\n")
            miner.fila_exploracao = miner.buscar_sementes()
            if not miner.fila_exploracao:
                log_func("Sem sementes disponiveis. Aguardando 15s...\n")
                for _ in range(30):
                    if stop_event.is_set():
                        break
                    time.sleep(0.5)
            continue

        proximo = miner.fila_exploracao.pop(0)

        if proximo in miner.visitados:
            continue

        try:
            miner.minerar_jogador(proximo)
            miner.visitados.add(proximo)
        except Exception as e:
            log_func(f"Erro: {e}\n")
            time.sleep(5)

    miner._salvar_fila_e_visitados()
    log_func("=== MINERADOR ENCERRADO ===\n")


# --- Execucao standalone (CLI) ---
if __name__ == "__main__":
    import sys
    stop_ev  = threading.Event()
    pause_ev = threading.Event()
    try:
        run_miner_loop(stop_ev, pause_ev)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario.")
        stop_ev.set()
