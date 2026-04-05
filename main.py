"""
Ponto de entrada do iLoL para Android.
Solicita permissões ANTES de qualquer import que acesse o disco.
"""
import sys
import os
import traceback


def salvar_crash(exc_text):
    candidates = [
        "/sdcard/ilol_crash.log",
        "/sdcard/Android/ilol_crash.log",
    ]
    for path in candidates:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(exc_text)
            return
        except Exception:
            continue


def mostrar_erro(erro):
    try:
        from kivy.app import App
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.label import Label

        class CrashApp(App):
            def build(self):
                sv = ScrollView()
                lbl = Label(
                    text="ERRO AO INICIAR:\n\n" + erro,
                    size_hint_y=None,
                    font_size="11sp",
                    halign="left",
                    valign="top",
                )
                lbl.bind(
                    width=lambda *x: lbl.setter("text_size")(lbl, (lbl.width, None)),
                    texture_size=lambda *x: lbl.setter("height")(lbl, lbl.texture_size[1]),
                )
                sv.add_widget(lbl)
                return sv

        CrashApp().run()
    except Exception:
        pass


try:
    # Solicita permissões de armazenamento ANTES de qualquer import
    # que tente acessar o disco (config.py, etc.)
    try:
        from android.permissions import request_permissions, Permission  # type: ignore
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except ImportError:
        pass  # não é Android

    from centro import ILoLApp
    ILoLApp().run()

except Exception:
    erro = traceback.format_exc()
    salvar_crash(erro)
    mostrar_erro(erro)
