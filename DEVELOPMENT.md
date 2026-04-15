# iLoL - Notas de Desenvolvimento

## Build e Distribuição

### APK Signing
- Usa keystore persistente para permitir updates "por cima" de versões anteriores
- Keystore: `ilol.keystore` (local) + GitHub Secret `KEYSTORE_B64`
- Alias: `ilol`
- Senha: `ilol2024`

### GitHub Actions
- Workflow: `.github/workflows/build.yml`
- Build: `buildozer android debug`
- Version code: automático via `github.run_number`
- APK output: `bin/*.apk`

### Secrets Necessários (GitHub Settings > Secrets > Actions)
| Nome | Valor |
|------|-------|
| `KEYSTORE_B64` | Base64 do ilol.keystore |
| `KEYSTORE_PASSWORD` | `ilol2024` |
| `KEY_ALIAS` | `ilol`

---

## Problemas Resolvidos

### [x] Conflito de packages em atualizações
- **Solução:** keystore fixo (`ilol.keystore`)

### [x] Erro PermissionError ao abrir app no Android
- **Causa:** `get_pasta()` usava `os.path.expanduser("~")` → resolvia para `/data/iLoL`
- **Solução inicial:** usar `android.storage` + `jnius` para pegar diretório privado do app

### [x] Pasta `/data/data/com.ilol/files/` inacessível para transferência manual de JSONs
- **Data:** 15/04/2026
- **Contexto:** Usuário conseguiu abrir o APK mas não conseguia colocar os arquivos JSON no app. A pasta usada era inacessível pelo gerenciador de arquivos.

#### Tentativa 1 — `getExternalFilesDir()` (Android/data/)
- **O que foi feito:** Mudar `get_pasta()` para usar `context.getExternalFilesDir(None)` que retorna `/storage/emulated/0/Android/data/com.ilol/files/`
- **Resultado:** ❌ **Falhou** — No Android 11+, a pasta `Android/data/` é escondida pelo sistema. Gerenciadores de arquivos comuns não mostram seu conteúdo.

#### Tentativa 2 — Fallback para `/data/data/com.ilol/files/` (interno)
- **O que foi feito:** Testar `context.getFilesDir()` como fallback
- **Resultado:** ❌ **Falhou** — Pasta interna do app, só acessível com root ou `adb shell run-as`. Transferência manual impossível.

#### Tentativa 3 — `os.path.expanduser("~")` → `/data/iLoL`
- **O que foi feito:** Usar fallback padrão do Python
- **Resultado:** ❌ **Falhou** — Android não permite escrita em `/data`. Erro `PermissionError`.

#### Tentativa 4 — `android.storage.app_storage_path()`
- **O que foi feito:** Usar módulo `android` do python-for-android
- **Resultado:** ❌ **Falhou** — Pode não estar disponível dependendo da versão do P4A/build.

#### ✅ Solução Final — Pasta no root do armazenamento interno (`/storage/emulated/0/iLoL/`)
- **O que foi feito:** Hardcoded `/storage/emulated/0/iLoL/` como caminho direto
- **Código (config.py):**
```python
def get_pasta():
    if _migration_module is not None and hasattr(_migration_module, "data_dir"):
        return _migration_module.data_dir
    if app_struct is not None and hasattr(app_struct, "data_dir"):
        return app_struct.data_dir

    # No Android, usa uma pasta no root do armazenamento interno
    # para que o usuario consiga copiar arquivos manualmente
    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        context = PythonActivity.mActivity

        # Tenta pegar o caminho do armazenamento externo primario
        external = context.getExternalFilesDir(None)
        if external is not None:
            # O Android retorna algo como:
            # /storage/emulated/0/Android/data/com.ilol/files
            # Usamos o root: /storage/emulated/0/iLoL
            # para que o usuario acesse facilmente pelo gerenciador de arquivos
            return "/storage/emulated/0/iLoL"

    except Exception:
        pass

    # Fallback direto
    return "/storage/emulated/0/iLoL"
```
- **Resultado:** ✅ **Funcionou** — Pasta visível e acessível por qualquer gerenciador de arquivos.

### [x] Transferência manual de JSONs sem usar ADB
- **Contexto:** Usuário não quer usar `adb push`. Quer baixar JSONs do Telegram e mover manualmente pelo celular.
- **Solução:** Pasta `/storage/emulated/0/iLoL/` fica no root do armazenamento interno. Usuário pode:
  1. Abrir o app uma vez → pasta é criada automaticamente
  2. Baixar `.json` do Telegram
  3. Usar gerenciador de arquivos para mover para `Armazenamento Interno/iLoL/`

### [x] Permissões de armazenamento em runtime (Android 11+)
- **Problema:** Android 11+ requer permissões em runtime para escrever em armazenamento externo
- **Solução (centro.py):**
```python
def _pedir_permissoes_android():
    """Solicita permissões de armazenamento em runtime (Android 11+)."""
    try:
        from android.permissions import Permission, request_permissions
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except ImportError:
        pass

_pedir_permissoes_android()
init_dados()
```

### [x] Mostrar caminho da pasta de dados na UI
- **O que foi feito:** Adicionado `_mostrar_caminho()` no `centro.py` que exibe o caminho na barra de status inferior
- **Código:**
```python
def _mostrar_caminho(self, *a):
    """Mostra o caminho da pasta de dados na tela."""
    try:
        from kivy.clock import Clock
        def _update(dt):
            self.status_lbl.text = f"Pasta: {PASTA}"
        Clock.schedule_once(_update, 0)
    except Exception:
        pass
```

### [x] Problema de persistência de edições no Windows
- **Problema:** As edições feitas via `edit` tool e `write_file` tool não estavam sendo detectadas pelo `git diff`. Os hashes dos arquivos eram idênticos ao HEAD.
- **Causa provável:** Cache do Windows / `core.filemode=false` / timestamps não atualizados
- **Solução:** Usar `write_file` para reescrever o arquivo completo + `copy /b file+,,` para forçar refresh do timestamp
- **Lição:** Em Windows, o `edit` tool pode não persistir mudanças. Usar `write_file` com conteúdo completo ou rodar `copy /b file+,,` antes de `git status`.

---

## Fluxo de Transferência de JSONs (Sem ADB)

```
┌─────────────────────────────────────────────────┐
│ 1. Instalar APK e abrir o app uma vez           │
│    → Pasta iLoL/ criada em /storage/emulated/0/ │
│                                                 │
│ 2. Baixar historico_partidas.json do Telegram   │
│    → Vai para pasta Downloads                   │
│                                                 │
│ 3. Abrir gerenciador de arquivos                │
│    → Selecionar Downloads/historico_partidas    │
│    → Mover para /storage/emulated/0/iLoL/       │
│                                                 │
│ 4. Reabrir o app                                │
│    → Dados carregados automaticamente           │
└─────────────────────────────────────────────────┘

📁 Armazenamento Interno/
 └── 📁 iLoL/
      ├── historico_partidas.json  ← usuário coloca manualmente
      ├── itens.json               ← copiado automaticamente pelo app
      ├── Campeoes.json            ← copiado automaticamente pelo app
      └── config.json              ← gerado automaticamente pelo app
```

---

## Inicialização de Dados

### Problema
- App não criava arquivos de dados (config.json, itens.json, historico_partidas.json) no Android
- Arquivos precisam ser copiados para diretório privado do app

### Solução
- `init_dados()` em config.py copia arquivos do app para diretório privado
- `carregar()` agora cria config.json se não existir
- Chamado automaticamente no startup do app (centro.py)

---

## Desenvolvimento Android

### Problema Original
- App não abria no Android: `PermissionError: Permission denied: '/data/iLoL'`

### Causa
- `get_pasta()` usava `os.path.join(os.path.expanduser("~"), "iLoL")` que resolve para `/data/iLoL`
- Android não permite escrita em `/data` para apps de usuário
- Tentativa de usar `platform.system()` falhou pois retorna "Linux" no Android (baseado em kernel Linux)

### Evolução da Solução
1. ❌ `android.storage.app_storage_path()` → pode não existir no build
2. ❌ `jnius getFilesDir()` → pasta interna inacessível
3. ❌ `getExternalFilesDir()` → `Android/data/` escondida no Android 11+
4. ✅ **Hardcoded `/storage/emulated/0/iLoL/`** → acessível por qualquer gerenciador

### Nota
- No build (GitHub Actions): módulos android/jnius não existem → usa fallback hardcoded
- No runtime (celular): módulos existem → tenta jnius mas retorna mesmo caminho hardcoded
- Ambos os caminhos convergem para `/storage/emulated/0/iLoL/`
