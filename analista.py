import json
import os
import sys

import config as cfg_mod
from utils import normalizar_champ, carregar_display_names

from config import get_pasta
PASTA = get_pasta()
MAPA_CLASSE = {
    "1": "Tank", "2": "Assassin", "3": "Mage",
    "4": "Marksman", "5": "Fighter", "6": "Support"
}

class AnalistaPro:
    def __init__(self, min_jogos=8):
        self.min_jogos = min_jogos
        self.path_hist = os.path.join(PASTA, "historico_partidas.json")
        self.path_item = os.path.join(PASTA, "itens.json")

        with open(self.path_hist, "r", encoding="utf-8") as f:
            self.partidas = json.load(f)
        with open(self.path_item, "r", encoding="utf-8") as f:
            self.db_itens = {int(k): v for k, v in json.load(f).items()}

    def analisar(self, champ_nome: str, entrada_classe: str):
        cfg = cfg_mod.carregar()
        BAN       = set(cfg["ban_ids"])
        preco_core = cfg["preco_core"]

        # FIX: normalizar nome para comparacao segura com Riot API (CamelCase)
        nome_norm  = normalizar_champ(champ_nome)
        classe_i   = MAPA_CLASSE.get(entrada_classe.strip(), entrada_classe.strip().capitalize())

        vits_item, total_item = {}, {}
        vits_geral, total_geral = 0, 0

        for p in self.partidas:
            if not isinstance(p, dict):
                continue
            # FIX: normalizar ambos os lados da comparacao
            if normalizar_champ(p.get("meu_campeao", "")) != nome_norm:
                continue
            if classe_i not in p.get("comp_inimiga_tags", []):
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
            print(f"\nSem dados suficientes para {champ_nome} vs {classe_i} ({total_geral} jogos).")
            return

        wr_base = (vits_geral / total_geral) * 100
        tudo = []

        for i_id, cont in total_item.items():
            if cont < self.min_jogos:
                continue
            info = self.db_itens.get(i_id, {})
            nome = info.get("nome", f"Item {i_id}")
            # FIX: usar campo "preco" (nao "gold" que nao existe no JSON)
            preco = info.get("preco", 0)
            tipo  = "CORE" if preco >= preco_core else "COMP."
            wr_i  = (vits_item[i_id] / cont) * 100
            efi   = wr_i - wr_base
            tudo.append({"nome": nome, "wr": wr_i, "jogos": cont, "efi": efi, "tipo": tipo})

        tudo.sort(key=lambda x: x["efi"], reverse=True)

        print("\n" + "=" * 75)
        print(f"RELATORIO: {champ_nome.upper()} vs {classe_i.upper()}")
        print(f"Amostra: {total_geral} partidas | WR Base: {wr_base:.1f}%")
        print("=" * 75)
        print(f"{'ITEM':<35} | {'TIPO':<7} | {'WR':>6} | {'JOGOS':>5} | {'EFI'}")
        print("-" * 75)
        for i in tudo:
            s = "+" if i["efi"] >= 0 else ""
            print(f"{i['nome']:<35} | {i['tipo']:<7} | {i['wr']:>5.1f}% | {i['jogos']:>5} | {s}{i['efi']:.1f}%")

        top = [x["nome"] for x in tudo if x["efi"] > 1.0 and x["tipo"] == "CORE"][:3]
        if top:
            print("\nBUILD SUGERIDA: " + " -> ".join(top))


if __name__ == "__main__":
    cfg = cfg_mod.carregar()
    app = AnalistaPro(min_jogos=cfg["min_jogos_analista"])
    c = input("Campeao: ")
    t = input("Classe (1=Tank 2=Assassin 3=Mage 4=Marksman 5=Fighter 6=Support): ")
    app.analisar(c, t)
