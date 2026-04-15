[app]
title           = ARAM Analyst
package.name    = ilol
package.domain  = com.ilol

source.dir      = .
source.include_exts = py,json,ttf
source.include_patterns = campeoes.json,itens.json,RobotoMono-Regular.ttf

version         = 2.0.0

android.keystore = ilol.keystore
android.keyalias = ilol

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

android.archs = arm64-v8a, armeabi-v7a

android.numeric_version = 10

[buildozer]
log_level = 2
warn_on_root = 1
