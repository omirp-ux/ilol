import json
import os
import shutil

from config import get_pasta
PASTA = get_pasta()

def reparar_json(log_func=print) -> bool:
    """
    Verifica e repara o historico_partidas.json.
    - Se OK: informa e retorna True sem alterar nada.
    - Se corrompido: tenta reparar, cria backup .bak e SOBRESCREVE o original diretamente.
    - Retorna True se OK ou reparado com sucesso, False se falhou.
    """
    nome_arquivo = os.path.join(PASTA, "historico_partidas.json")
    nome_bak     = os.path.join(PASTA, "historico_partidas.bak")

    if not os.path.exists(nome_arquivo):
        log_func("Arquivo historico_partidas.json nao encontrado!\n")
        return False

    log_func("Analisando historico_partidas.json...\n")

    # Lê o conteúdo inteiro para memória e fecha o handle imediatamente
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read().strip()

    # --- Verifica se o arquivo já está íntegro ---
    try:
        dados = json.loads(conteudo)
        log_func(f"OK! {len(dados):,} partidas registradas. Nenhum reparo necessario.\n")
        return True
    except json.JSONDecodeError:
        log_func("JSON corrompido detectado. Iniciando reparo...\n")

    # --- Tenta fechar o JSON cortado ---
    if not conteudo.endswith("]"):
        pos = conteudo.rfind("}")
        if pos == -1:
            log_func("Reparo impossivel: estrutura muito danificada.\n")
            return False
        conteudo = conteudo[: pos + 1] + "]"

    try:
        dados = json.loads(conteudo)
        log_func(f"{len(dados):,} partidas recuperadas!\n")

        # Cria backup do arquivo corrompido antes de qualquer escrita
        shutil.copy2(nome_arquivo, nome_bak)
        log_func("Backup salvo em: historico_partidas.bak\n")

        # Sobrescreve o original diretamente — sem arquivo temporário nem rename.
        # Os dados já estão na memória, então não há conflito de handles.
        # Esta abordagem evita WinError 5 e WinError 32 no Windows.
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        log_func("Arquivo reparado e salvo com sucesso!\n")
        log_func("Sistema pronto para uso.\n")
        return True

    except Exception as e:
        log_func(f"Erro critico no reparo: {e}\n")
        return False


if __name__ == "__main__":
    reparar_json()
