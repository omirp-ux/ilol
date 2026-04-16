import json
import os
import sys

import config as cfg_mod
from utils import normalizar_champ

from config import get_pasta

class PowerSpikeAnalyst:
    def __init__(self):
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

    def analisar_curva_de_poder(self, meu_champ: str):
        cfg = cfg_mod.carregar()
        BAN        = set(cfg["ban_ids"])
        preco_core = cfg["preco_core"]

        # FIX: normalizar nome para comparacao segura
        nome_norm = normalizar_champ(meu_champ)

        curva = {i: {"vits": 0, "total": 0} for i in range(1, 7)}
        total_jogos = 0

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            # FIX: comparacao normalizada
            if normalizar_champ(p.get("meu_campeao", "")) != nome_norm:
                continue

            meus_itens = p.get("itens", [])
            qtd_cores  = sum(
                1 for i_id in meus_itens
                if i_id and i_id not in BAN
                and self.db_itens.get(i_id, {}).get("preco", 0) >= preco_core
            )

            if qtd_cores > 0:
                idx = min(qtd_cores, 6)
                curva[idx]["total"] += 1
                if p.get("vitoria"):
                    curva[idx]["vits"] += 1
                total_jogos += 1

        if total_jogos == 0:
            print(f"Nenhum dado encontrado para {meu_champ}.")
            return

        print("\n" + "=" * 65)
        print(f"CURVA DE PODER (POWER SPIKE): {meu_champ.upper()}")
        print(f"Baseado em {total_jogos} partidas")
        print("=" * 65)
        print(f"{'QUANTIDADE DE ITENS':<25} | {'WINRATE':>10} | {'JOGOS'}")
        print("-" * 65)

        for qtd in range(1, 7):
            total = curva[qtd]["total"]
            if total == 0:
                continue
            wr = (curva[qtd]["vits"] / total) * 100
            if qtd == 1:
                label = "(Early Game)"
            elif qtd <= 3:
                label = "(Mid Game)"
            else:
                label = "(Late Game)"
            desc = f"{qtd} Item(s) {label}"
            print(f"{desc:<25} | {wr:>9.1f}% | {total:>5}")

        print("=" * 65)


if __name__ == "__main__":
    analista = PowerSpikeAnalyst()
    print("\n=== POWER SPIKE ANALYST ===")
    c = input("Analisar curva de poder de qual campeao?: ")
    analista.analisar_curva_de_poder(c)
