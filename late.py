import json
import os
import sys

import config as cfg_mod
from utils import normalizar_champ

from config import get_pasta

class LateGameAnalyst:
    def __init__(self, min_jogos=3):
        self.min_jogos = min_jogos
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

    def analisar_late_game(self, meu_champ: str, comp_inimiga: dict):
        cfg = cfg_mod.carregar()
        BAN        = set(cfg["ban_ids"])
        preco_core = cfg["preco_core"]

        # FIX: normalizar nome para comparacao segura
        nome_norm = normalizar_champ(meu_champ)
        stats_item = {}
        total_late = 0

        print(f"\nAnalisando itens de LATE GAME para {meu_champ.upper()}...")

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            # FIX: comparacao normalizada
            if normalizar_champ(p.get("meu_campeao", "")) != nome_norm:
                continue

            tags_partida = p.get("comp_inimiga_tags", [])
            if not all(tags_partida.count(cl) >= qtd for cl, qtd in comp_inimiga.items()):
                continue

            meus_itens = p.get("itens", [])

            # Itens finalizados
            itens_finais = [
                i_id for i_id in meus_itens
                if i_id and i_id not in BAN
                and self.db_itens.get(i_id, {}).get("preco", 0) >= preco_core
            ]

            # Foco em partidas com 4+ itens (late game real)
            if len(itens_finais) >= 4:
                total_late += 1
                vit = 1 if p.get("vitoria") else 0

                # 4o item em diante = late game
                for i_id in itens_finais[3:]:
                    if i_id not in stats_item:
                        stats_item[i_id] = {"vits": 0, "total": 0}
                    stats_item[i_id]["total"] += 1
                    stats_item[i_id]["vits"]  += vit

        if not stats_item:
            print(f"Dados insuficientes para late game com {meu_champ}.")
            return

        ranking = []
        for i_id, dado in stats_item.items():
            if dado["total"] < self.min_jogos:
                continue
            wr   = (dado["vits"] / dado["total"]) * 100
            nome = self.db_itens.get(i_id, {}).get("nome", f"ID:{i_id}")
            ranking.append({"nome": nome, "wr": wr, "jogos": dado["total"]})

        ranking.sort(key=lambda x: x["wr"], reverse=True)

        print("=" * 80)
        print(f"MELHORES ITENS PARA 4o, 5o e 6o SLOT | Amostra: {total_late} jogos")
        print("=" * 80)
        print(f"{'ITEM DE LATE GAME':<40} | {'WINRATE':>8} | {'APARICOES'}")
        print("-" * 80)
        for r in ranking[:15]:
            print(f"{r['nome']:<40} | {r['wr']:>7.1f}% | {r['jogos']:>9}")
        print("=" * 80)


if __name__ == "__main__":
    cfg = cfg_mod.carregar()
    analista = LateGameAnalyst(min_jogos=cfg["min_jogos_late"])
    print("\n=== LATE GAME SPECIALIST ===")
    c = input("Seu Campeao: ")
    comp = {}
    for cl in ["Tank", "Assassin", "Mage", "Marksman", "Fighter", "Support"]:
        qtd = input(f"Pelo menos quantos {cl}s? ")
        if qtd.isdigit() and int(qtd) > 0:
            comp[cl] = int(qtd)
    analista.analisar_late_game(c, comp)
