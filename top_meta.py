import json
import os
import sys

import config as cfg_mod
from utils import normalizar_champ, carregar_display_names

from config import get_pasta

class MetaAnalyzer:
    def __init__(self, min_aparicoes=15):
        self.min_aparicoes = min_aparicoes
        self.path_hist = os.path.join(PASTA, "historico_partidas.json")
        self.display_names = carregar_display_names(PASTA)

        if not os.path.exists(self.path_hist):
            print(f"Erro: {self.path_hist} nao encontrado!")
            sys.exit()
        try:
            with open(self.path_hist, "r", encoding="utf-8") as f:
                self.partidas = json.load(f)
        except json.JSONDecodeError:
            print("Erro: JSON corrompido. Rode a funcao Reparar Dados.")
            sys.exit()

    def gerar_tier_list(self, tamanho_top=10):
        cfg = cfg_mod.carregar()
        stats = {}

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            meu = p.get("meu_campeao")
            if not meu or not isinstance(meu, str):
                continue

            # FIX: normalizar para evitar duplicatas por CamelCase vs espacos
            nome_norm = normalizar_champ(meu)
            nome_display = self.display_names.get(nome_norm, meu)

            vit = 1 if p.get("vitoria") else 0

            if nome_display not in stats:
                stats[nome_display] = {"vits": 0, "total": 0}
            stats[nome_display]["vits"] += vit
            stats[nome_display]["total"] += 1

        lista_final = []
        min_ap = cfg.get("min_aparicoes_meta", self.min_aparicoes)
        for nome, dado in stats.items():
            if dado["total"] < min_ap:
                continue
            wr = (dado["vits"] / dado["total"]) * 100
            lista_final.append({"nome": nome, "wr": wr, "jogos": dado["total"]})

        if not lista_final:
            print(f"Sem dados suficientes (Minimo: {min_ap} jogos).")
            return

        top_lista = sorted(lista_final, key=lambda x: x["wr"], reverse=True)[:tamanho_top]
        mais_jogados = sorted(lista_final, key=lambda x: x["jogos"], reverse=True)[:30]
        baits = sorted(mais_jogados, key=lambda x: x["wr"])[:tamanho_top]

        print("\n" + "=" * 60)
        print(f"RANKING ARAM/MAYHEM - TOP {tamanho_top}")
        print("=" * 60)
        print(f"\nOS {tamanho_top} MELHORES (Winrate)")
        print("-" * 60)
        print(f"{'CAMPEAO':<22} | {'WR':>8} | {'JOGOS':>6}")
        for i, c in enumerate(top_lista, 1):
            print(f"{i}. {c['nome']:<19} | {c['wr']:>7.1f}% | {c['jogos']:>6}")

        print(f"\nOS {tamanho_top} MAIORES BAITS (Populares que Perdem)")
        print("-" * 60)
        print(f"{'CAMPEAO':<22} | {'WR':>8} | {'JOGOS':>6}")
        for i, b in enumerate(baits, 1):
            print(f"{i}. {b['nome']:<19} | {b['wr']:>7.1f}% | {b['jogos']:>6}")
        print("=" * 60)


if __name__ == "__main__":
    cfg = cfg_mod.carregar()
    meta = MetaAnalyzer(min_aparicoes=cfg["min_aparicoes_meta"])
    print("\n=== META ANALYZER ===")
    try:
        t = input("Tamanho do Top (ex: 5, 10, 20): ")
        tamanho = int(t) if t.isdigit() else 10
    except Exception:
        tamanho = 10
    meta.gerar_tier_list(tamanho)
