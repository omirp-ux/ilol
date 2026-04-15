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
| `KEY_ALIAS` | `ilol` |

## Problemas Resolvidos
- [x] Conflito de packages em atualizações - resolvido com keystore fixo
- [x] Erro PermissionError ao abrir app no Android - resolvido com android.storage/jnius

## Desenvolvimento Android

### Problema
- App não abria no Android: `PermissionError: Permission denied: '/data/iLoL'`

### Causa
- `get_pasta()` usava `os.path.join(os.path.expanduser("~"), "iLoL")` que resolve para `/data/iLoL`
- Android não permite escrita em `/data` para apps de usuário
- Tentativa de usar `platform.system()` falhou pois retorna "Linux" no Android (baseado em kernel Linux)

### Solução (config.py)
```python
def get_pasta():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except (ImportError, AttributeError):
        pass
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        return PythonActivity.mActivity.getFilesDir().getAbsolutePath()
    except (ImportError, AttributeError):
        pass
    return os.path.join(os.path.expanduser("~"), "iLoL")
```

### Nota
- No build (GitHub Actions): módulos android/jnius não existem → usa fallback
- No runtime (celular): módulos existem → usa diretório privado do app

## Inicialização de Dados

### Problema
- App não criava arquivos de dados (config.json, itens.json, historico_partidas.json) no Android
- Arquivos precisam ser copiados para diretório privado do app

### Solução
- `init_dados()` em config.py copia arquivos do app para diretório privado
- `carregar()` agora cria config.json se não existir
- Chamado automaticamente no startup do app (centro.py)
