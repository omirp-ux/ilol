import json
import os
import sys

import config as cfg_mod
from utils import normalizar_champ

from config import get_pasta
PASTA = get_pasta()

class AnalistaComposicao:
    def __init__(self, min_jogos=3):
        self.min_jogos = min_jogos
        self.path_hist = os.path.join(PASTA, "historico_partidas.json")
        self.path_item = os.path.join(PASTA, "itens.json")

        with open(self.path_hist, "r", encoding="utf-8") as f:
            self.partidas = json.load(f)
        with open(self.path_item, "r", encoding="utf-8") as f:
            self.db_itens = {int(k): v for k, v in json.load(f).items()}

    def analisar_comp(self, meu_champ: str, comp_escolhida: dict):
        cfg = cfg_mod.carregar()
        BAN        = set(cfg["ban_ids"])
        preco_core = cfg["preco_core"]

        # FIX: normalizar nome para comparacao segura com Riot API
        nome_norm = normalizar_champ(meu_champ)

        vits_item, total_item = {}, {}
        vits_geral, total_geral = 0, 0

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            # FIX: comparacao normalizada
            if normalizar_champ(p.get("meu_campeao", "")) != nome_norm:
                continue

            tags_partida = p.get("comp_inimiga_tags", [])
            match = all(tags_partida.count(cl) >= qtd for cl, qtd in comp_escolhida.items())
            if not match:
                continue

            total_geral += 1
            if p.get("vitoria"):
                vits_geral += 1

            for i_id in p.get("itens", []):
                if not i_id or i_id in BAN:
                    continue
                total_item[i_id] = total_item.get(i_id, 0) + 1
                vits_item[i_id]  = vits_item.get(i_id, 0) + (1 if p.get("vitoria") else 0)

        if total_geral < 2:
            print(f"\nDados insuficientes ({total_geral} jogos).")
            return

        wr_base = (vits_geral / total_geral) * 100
        rank = []
        for i_id, cont in total_item.items():
            if cont < self.min_jogos:
                continue
            info = self.db_itens.get(i_id, {})
            wr_i = (vits_item[i_id] / cont) * 100
            efi  = wr_i - wr_base
            rank.append({
                "nome":  info.get("nome", f"Item {i_id}"),
                "wr":    wr_i,
                "jogos": cont,
                "efi":   efi,
            })

        rank.sort(key=lambda x: x["efi"], reverse=True)

        print("\n" + "=" * 80)
        print(f"ANALISE ESTRATEGICA - Amostra: {total_geral} partidas")
        print(f"Winrate Base contra esta comp: {wr_base:.1f}%")
        print("=" * 80)
        print(f"{'ITEM':<35} | {'WR':>6} | {'JOGOS':>5} | {'EFI'}")
        print("-" * 80)
        for i in rank[:15]:
            s = "+" if i["efi"] >= 0 else ""
            print(f"{i['nome']:<35} | {i['wr']:>5.1f}% | {i['jogos']:>5} | {s}{i['efi']:.1f}%")


if __name__ == "__main__":
    cfg = cfg_mod.carregar()
    analista = AnalistaComposicao(min_jogos=cfg["min_jogos_comp"])
    print("=== ANALISTA DE COMPOSICAO ===")
    meu = input("Seu Campeao: ")
    comp = {}
    for c in ["Tank", "Assassin", "Mage", "Marksman", "Fighter", "Support"]:
        qtd = input(f"Pelo menos quantos {c}s? (Vazio = 0): ")
        if qtd.isdigit() and int(qtd) > 0:
            comp[c] = int(qtd)
    analista.analisar_comp(meu, comp)
