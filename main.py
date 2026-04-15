import traceback


def salvar_crash(exc_text):
    for path in ["/sdcard/ilol_crash.log"]:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(exc_text)
            return
        except Exception:
            pass


def mostrar_erro(erro):
    try:
        from kivy.app import App
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.label import Label

        class CrashApp(App):
            def build(self):
                sv = ScrollView()
                lbl = Label(
                    text="ERRO:\n\n" + erro,
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
    from centro import _pedir_permissoes_android, _run_app
    _pedir_permissoes_android(_run_app)
except Exception:
    erro = traceback.format_exc()
    salvar_crash(erro)
    mostrar_erro(erro)
