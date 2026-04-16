import json
import os
import sys
from itertools import combinations

import config as cfg_mod
from utils import normalizar_champ

from config import get_pasta

class CoreAnalyst:
    def __init__(self, min_comb=2):
        self.min_comb = min_comb
        self.path_hist = os.path.join(PASTA, "historico_partidas.json")
        self.path_item = os.path.join(PASTA, "itens.json")

        try:
            with open(self.path_hist, "r", encoding="utf-8") as f:
                self.partidas = json.load(f)
            with open(self.path_item, "r", encoding="utf-8") as f:
                self.db_itens = {int(k): v for k, v in json.load(f).items()}
        except Exception as e:
            print(f"Erro ao carregar arquivos: {e}")
            sys.exit()

    def analisar_core(self, meu_champ: str, comp_inimiga: dict):
        cfg = cfg_mod.carregar()
        BAN        = set(cfg["ban_ids"])
        preco_core = cfg["preco_core"]

        # FIX: normalizar nome para comparacao segura
        nome_norm = normalizar_champ(meu_champ)
        comb_stats = {}
        total_filtro = 0

        print(f"\nBuscando melhores combinacoes de 3 itens para {meu_champ.upper()}...")

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            # FIX: comparacao normalizada
            if normalizar_champ(p.get("meu_campeao", "")) != nome_norm:
                continue

            tags_partida = p.get("comp_inimiga_tags", [])
            if not all(tags_partida.count(cl) >= qtd for cl, qtd in comp_inimiga.items()):
                continue

            total_filtro += 1
            meus_itens = p.get("itens", [])

            # FIX: considera apenas itens finalizados pelo preco (sem depender do campo "into")
            cores_na_partida = []
            for i_id in meus_itens:
                if not i_id or i_id in BAN:
                    continue
                info  = self.db_itens.get(i_id, {})
                valor = info.get("preco", 0)
                # FIX: criterio unico e correto — so itens com preco >= preco_core
                if valor >= preco_core:
                    cores_na_partida.append(i_id)

            if len(cores_na_partida) >= 3:
                for combo in combinations(sorted(cores_na_partida), 3):
                    if combo not in comb_stats:
                        comb_stats[combo] = {"vits": 0, "total": 0}
                    comb_stats[combo]["total"] += 1
                    if p.get("vitoria"):
                        comb_stats[combo]["vits"] += 1

        if not comb_stats:
            print(f"Nenhuma build de 3 itens encontrada em {total_filtro} partidas.")
            print("Dica: Talvez voce esteja fechando os jogos antes do 3o item!")
            return

        ranking = []
        for combo, dado in comb_stats.items():
            if dado["total"] < self.min_comb:
                continue
            wr    = (dado["vits"] / dado["total"]) * 100
            nomes = [self.db_itens.get(i_id, {}).get("nome", f"ID:{i_id}") for i_id in combo]
            ranking.append({"nomes": nomes, "wr": wr, "jogos": dado["total"]})

        ranking.sort(key=lambda x: (x["wr"], x["jogos"]), reverse=True)

        print("=" * 100)
        print(f"TOP CORE BUILDS - Amostra: {total_filtro} jogos | Min: {self.min_comb} jogos/build")
        print("=" * 100)
        print(f"{'COMBINACAO DE 3 ITENS':<75} | {'WR':>6} | {'JOGOS'}")
        print("-" * 100)
        for r in ranking[:15]:
            itens_str = " + ".join(r["nomes"])
            print(f"{itens_str[:75]:<75} | {r['wr']:>5.1f}% | {r['jogos']:>5}")


if __name__ == "__main__":
    cfg = cfg_mod.carregar()
    analista = CoreAnalyst(min_comb=cfg["min_jogos_core"])
    print("\n=== CORE BUILD FINDER ===")
    c = input("Seu Campeao: ")
    comp = {}
    for cl in ["Tank", "Assassin", "Mage", "Marksman", "Fighter", "Support"]:
        qtd = input(f"Pelo menos quantos {cl}s? ")
        if qtd.isdigit() and int(qtd) > 0:
            comp[cl] = int(qtd)
    analista.analisar_core(c, comp)
