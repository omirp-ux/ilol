[app]
title           = ARAM Analyst
package.name    = ilol
package.domain  = com.ilol

source.dir      = .
source.include_exts = py,json
source.include_patterns = campeoes.json,itens.json

version         = 1.0

# Ponto de entrada
entrypoint = centro.py

requirements =
    python3,
    kivy==2.3.0,
    kivymd==1.2.0,
    requests,
    android,
    certifi,
    charset-normalizer,
    urllib3,
    idna

orientation = portrait
fullscreen  = 0

android.permissions =
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    MANAGE_EXTERNAL_STORAGE

android.api     = 33
android.minapi  = 26
android.ndk     = 25b
android.sdk     = 33

android.archs = arm64-v8a, armeabi-v7a

# Ícone e splash (opcional — coloque icon.png e presplash.png na raiz se quiser)
# icon.filename     = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
