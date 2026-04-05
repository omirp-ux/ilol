"""
Ponto de entrada do iLoL para Android.
Captura qualquer erro de importacao/execucao e salva em crash.log.
"""
import sys
import os
import traceback


def salvar_crash(exc_text):
    candidates = [
        "/sdcard/ilol_crash.log",
        "/sdcard/Android/ilol_crash.log",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash.log"),
    ]
    for path in candidates:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(exc_text)
            return path
        except Exception:
            continue
    return None


try:
    from centro import ILoLApp
    ILoLApp().run()

except Exception:
    erro = traceback.format_exc()
    salvar_crash(erro)

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
