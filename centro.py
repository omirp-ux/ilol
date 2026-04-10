"""
ARAM Analyst — Centro de Comando (Mobile/KivyMD)
Execute com: python main.py
"""
import sys
import io
import os
import threading
import queue

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.metrics import dp, sp

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabs, MDTabsBase

from config import get_pasta
import config as cfg_mod

PASTA   = get_pasta()
CLASSES = ["Tank", "Assassin", "Mage", "Marksman", "Fighter", "Support"]


# ─────────────────────────────────────────────────────────────────────────────
#  Widgets auxiliares
# ─────────────────────────────────────────────────────────────────────────────

class LogOutput(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size=sp(11),
            padding=(dp(8), dp(8)),
            color=(0.88, 0.88, 0.88, 1),
        )
        self._label.bind(
            width=lambda *x: self._label.setter("text_size")(
                self._label, (self._label.width, None)
            ),
            texture_size=lambda *x: self._label.setter("height")(
                self._label, self._label.texture_size[1]
            ),
        )
        self.add_widget(self._label)

    def append(self, text: str):
        def _do(dt):
            self._label.text += text
            self.scroll_y = 0
        Clock.schedule_once(_do, 0)

    def set_text(self, text: str):
        def _do(dt):
            self._label.text = text.strip() or "(sem resultado)"
            self.scroll_y = 1
        Clock.schedule_once(_do, 0)

    def clear(self, *a):
        Clock.schedule_once(
            lambda dt: self._label.setter("text")(self._label, ""), 0
        )


class IntField(BoxLayout):
    """Campo numerico com botoes - e +."""
    def __init__(self, min_val=0, max_val=9999, value=0, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(2),
            **kwargs,
        )
        self.min_val = min_val
        self.max_val = max_val

        self._btn_m = MDIconButton(
            icon="minus",
            on_release=self._dec,
            size_hint=(None, 1),
            width=dp(36),
        )
        self._field = MDTextField(
            text=str(value),
            input_filter="int",
            size_hint=(None, None),
            width=dp(64),
            height=dp(44),
            halign="center",
        )
        self._btn_p = MDIconButton(
            icon="plus",
            on_release=self._inc,
            size_hint=(None, 1),
            width=dp(36),
        )
        self.add_widget(self._btn_m)
        self.add_widget(self._field)
        self.add_widget(self._btn_p)

    def _inc(self, *a):
        v = self.get() + 1
        if v <= self.max_val:
            self._field.text = str(v)

    def _dec(self, *a):
        v = self.get() - 1
        if v >= self.min_val:
            self._field.text = str(v)

    def get(self) -> int:
        try:
            return int(self._field.text or 0)
        except ValueError:
            return self.min_val

    def set(self, value: int):
        self._field.text = str(value)


class Tab(FloatLayout, MDTabsBase):
    pass


# ─────────────────────────────────────────────────────────────────────────────
#  Aplicativo principal
# ─────────────────────────────────────────────────────────────────────────────

class ILoLApp(MDApp):

    def build(self):
        self.title = "ARAM Analyst"
        self.theme_cls.theme_style     = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.cfg = cfg_mod.carregar()

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(title="ARAM Analyst", elevation=4))

        tabs = MDTabs(allow_stretch=True, anim_duration=0.15)
        tab_defs = [
            ("Config",      self._build_tab_config),
            ("Meta",        self._build_tab_meta),
            ("Analista",    self._build_tab_analista),
            ("Composicao",  self._build_tab_comp),
            ("Core Build",  self._build_tab_core),
            ("Late Game",   self._build_tab_late),
            ("Pw. Spike",   self._build_tab_spike),
            ("Reparar",     self._build_tab_repair),
        ]
        for name, builder in tab_defs:
            tab = Tab(title=name)
            tab.add_widget(builder())
            tabs.add_widget(tab)
        root.add_widget(tabs)

        # Status bar
        status_row = BoxLayout(size_hint_y=None, height=dp(28))
        self.status_lbl = MDLabel(
            text="Pronto.",
            font_style="Caption",
            padding=(dp(8), 0),
        )
        self.banco_lbl = MDLabel(
            text="Banco: —",
            font_style="Caption",
            halign="right",
            padding=(dp(8), 0),
            size_hint_x=0.5,
        )
        status_row.add_widget(self.status_lbl)
        status_row.add_widget(self.banco_lbl)
        root.add_widget(status_row)

        Clock.schedule_interval(lambda dt: self._atualizar_banco(), 5)
        Clock.schedule_once(lambda dt: self._atualizar_banco(), 0.5)

        return root

    def _atualizar_banco(self, *a):
        from utils import contar_partidas
        n = contar_partidas(PASTA)
        if n == -1:
            self.banco_lbl.text = "Banco: CORROMPIDO"
        elif n == 0:
            self.banco_lbl.text = "Banco: vazio"
        else:
            self.banco_lbl.text = f"Banco: {n:,} partidas"

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Config
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_config(self):
        sv = ScrollView()
        lay = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(10),
        )
        lay.bind(minimum_height=lay.setter("height"))

        lay.add_widget(MDLabel(
            text="Configuracoes do Sistema",
            font_style="H6",
            size_hint_y=None,
            height=dp(36),
        ))

        # API Key
        lay.add_widget(MDLabel(
            text="Riot API Key",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(28),
        ))

        api_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.api_field = MDTextField(
            text=self.cfg.get("api_key", ""),
            hint_text="RGAPI-xxxxxxxx-...",
            password=True,
            size_hint_y=None,
            height=dp(48),
        )
        self._api_visible = False
        self.btn_eye = MDIconButton(
            icon="eye",
            on_release=self._toggle_api_vis,
            size_hint=(None, 1),
            width=dp(48),
        )
        api_row.add_widget(self.api_field)
        api_row.add_widget(self.btn_eye)
        lay.add_widget(api_row)

        # Parametros numericos
        lay.add_widget(MDLabel(
            text="Parametros de Analise",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(32),
        ))

        params = [
            ("Preco minimo de item finalizado", "preco_core",         2000),
            ("Min. jogos — Analista vs Classe", "min_jogos_analista", 8),
            ("Min. jogos — Composicao",         "min_jogos_comp",     3),
            ("Min. jogos — Core Build",         "min_jogos_core",     2),
            ("Min. jogos — Late Game",          "min_jogos_late",     2),
            ("Min. aparicoes — Tier List",      "min_aparicoes_meta", 15),
        ]
        self.param_fields = {}
        for label, key, default in params:
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
            row.add_widget(MDLabel(text=label, size_hint_x=0.65, halign="left"))
            f = IntField(value=self.cfg.get(key, default))
            self.param_fields[key] = f
            row.add_widget(f)
            lay.add_widget(row)

        lay.add_widget(MDRaisedButton(
            text="Salvar Configuracoes",
            size_hint_y=None,
            height=dp(48),
            on_release=self._salvar_config,
        ))

        sv.add_widget(lay)
        return sv

    def _toggle_api_vis(self, *a):
        self._api_visible = not self._api_visible
        self.api_field.password = not self._api_visible
        self.btn_eye.icon = "eye-off" if self._api_visible else "eye"

    def _salvar_config(self, *a):
        self.cfg["api_key"] = self.api_field.text.strip()
        for key, field in self.param_fields.items():
            self.cfg[key] = field.get()
        cfg_mod.salvar(self.cfg)
        self.status_lbl.text = "Configuracoes salvas!"
        Snackbar(text="Configuracoes salvas com sucesso!").open()

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Meta
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_meta(self):
        lay = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        row.add_widget(MDLabel(text="Tamanho do Top:", size_hint_x=0.55))
        self.meta_top = IntField(min_val=3, max_val=50, value=10)
        row.add_widget(self.meta_top)
        lay.add_widget(row)

        lay.add_widget(MDRaisedButton(
            text="Gerar Tier List",
            size_hint_y=None,
            height=dp(48),
            on_release=self._run_meta,
        ))
        self.meta_out = LogOutput()
        lay.add_widget(self.meta_out)
        return lay

    def _run_meta(self, *a):
        def worker():
            self.cfg = cfg_mod.carregar()
            from top_meta import MetaAnalyzer
            ana = MetaAnalyzer(min_aparicoes=self.cfg["min_aparicoes_meta"])
            self.meta_out.set_text(self._capture(ana.gerar_tier_list, self.meta_top.get()))
            self._done()
        self._run_thread(worker, "Gerando tier list...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Analista
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_analista(self):
        lay = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        self.ana_champ = MDTextField(
            hint_text="Campeao",
            size_hint_y=None,
            height=dp(48),
        )
        lay.add_widget(self.ana_champ)

        lay.add_widget(MDLabel(
            text="Classe inimiga:",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(26),
        ))

        self._ana_class = "Tank"
        self._ana_btns  = {}
        grid = GridLayout(cols=3, size_hint_y=None, height=dp(108), spacing=dp(6))
        for cl in CLASSES:
            btn = MDRaisedButton(
                text=cl,
                on_release=lambda x, c=cl: self._sel_ana(c),
            )
            self._ana_btns[cl] = btn
            grid.add_widget(btn)
        lay.add_widget(grid)
        self._sel_ana("Tank")

        lay.add_widget(MDRaisedButton(
            text="Analisar",
            size_hint_y=None,
            height=dp(48),
            on_release=self._run_analista,
        ))
        self.ana_out = LogOutput()
        lay.add_widget(self.ana_out)
        return lay

    def _sel_ana(self, classe: str):
        self._ana_class = classe
        PRIMARY = self.theme_cls.primary_color
        DARK    = self.theme_cls.primary_dark
        for cl, btn in self._ana_btns.items():
            btn.md_bg_color = PRIMARY if cl == classe else DARK

    def _run_analista(self, *a):
        def worker():
            self.cfg = cfg_mod.carregar()
            from analista import AnalistaPro
            ana = AnalistaPro(min_jogos=self.cfg["min_jogos_analista"])
            self.ana_out.set_text(
                self._capture(ana.analisar, self.ana_champ.text, self._ana_class)
            )
            self._done()
        self._run_thread(worker, "Analisando...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Composicao
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_comp(self):
        lay, champ, fields, out = self._multi_classe_layout(
            btn_label="Analisar Composicao",
            btn_callback=self._run_comp,
        )
        self.comp_champ  = champ
        self.comp_fields = fields
        self.comp_out    = out
        return lay

    def _run_comp(self, *a):
        def worker():
            self.cfg = cfg_mod.carregar()
            from analista2 import AnalistaComposicao
            ana  = AnalistaComposicao(min_jogos=self.cfg["min_jogos_comp"])
            comp = self._ler_comp(self.comp_fields)
            self.comp_out.set_text(
                self._capture(ana.analisar_comp, self.comp_champ.text, comp)
            )
            self._done()
        self._run_thread(worker, "Analisando composicao...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Core Build
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_core(self):
        lay, champ, fields, out = self._multi_classe_layout(
            btn_label="Buscar Core Build",
            btn_callback=self._run_core,
        )
        self.core_champ  = champ
        self.core_fields = fields
        self.core_out    = out
        return lay

    def _run_core(self, *a):
        def worker():
            self.cfg = cfg_mod.carregar()
            from core import CoreAnalyst
            ana  = CoreAnalyst(min_comb=self.cfg["min_jogos_core"])
            comp = self._ler_comp(self.core_fields)
            self.core_out.set_text(
                self._capture(ana.analisar_core, self.core_champ.text, comp)
            )
            self._done()
        self._run_thread(worker, "Analisando core builds...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Late Game
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_late(self):
        lay, champ, fields, out = self._multi_classe_layout(
            btn_label="Analisar Late Game",
            btn_callback=self._run_late,
        )
        self.late_champ  = champ
        self.late_fields = fields
        self.late_out    = out
        return lay

    def _run_late(self, *a):
        def worker():
            self.cfg = cfg_mod.carregar()
            from late import LateGameAnalyst
            ana  = LateGameAnalyst(min_jogos=self.cfg["min_jogos_late"])
            comp = self._ler_comp(self.late_fields)
            self.late_out.set_text(
                self._capture(ana.analisar_late_game, self.late_champ.text, comp)
            )
            self._done()
        self._run_thread(worker, "Analisando late game...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Power Spike
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_spike(self):
        lay = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        self.spike_champ = MDTextField(
            hint_text="Campeao",
            size_hint_y=None,
            height=dp(48),
        )
        lay.add_widget(self.spike_champ)
        lay.add_widget(MDRaisedButton(
            text="Analisar Power Spike",
            size_hint_y=None,
            height=dp(48),
            on_release=self._run_spike,
        ))
        self.spike_out = LogOutput()
        lay.add_widget(self.spike_out)
        return lay

    def _run_spike(self, *a):
        def worker():
            from powerspike import PowerSpikeAnalyst
            ana = PowerSpikeAnalyst()
            self.spike_out.set_text(
                self._capture(ana.analisar_curva_de_poder, self.spike_champ.text)
            )
            self._done()
        self._run_thread(worker, "Calculando power spike...")

    # ─────────────────────────────────────────────────────────────────────────
    #  ABA: Reparar
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_repair(self):
        lay = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        info = (
            "Verifica e repara o historico_partidas.json caso tenha sido\n"
            "interrompido no meio de uma mineracao.\n\n"
            "- Arquivo corrompido e substituido automaticamente.\n"
            "- Backup criado como historico_partidas.bak.\n"
        )
        lay.add_widget(MDLabel(
            text=info,
            size_hint_y=None,
            height=dp(130),
            halign="left",
        ))

        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row.add_widget(MDRaisedButton(
            text="Reparar Agora",
            on_release=self._run_repair,
        ))
        row.add_widget(MDFlatButton(
            text="Limpar Log",
            on_release=lambda *a: self.repair_out.clear(),
        ))
        lay.add_widget(row)

        self.repair_out = LogOutput()
        lay.add_widget(self.repair_out)
        return lay

    def _run_repair(self, *a):
        def worker():
            from reparar_dados import reparar_json
            q = queue.Queue()
            reparar_json(log_func=lambda t: q.put(t))
            result = ""
            while not q.empty():
                result += q.get()
            self.repair_out.set_text(result)
            Clock.schedule_once(lambda dt: self._atualizar_banco(), 0)
            self._done()
        self._run_thread(worker, "Reparando dados...")

    # ─────────────────────────────────────────────────────────────────────────
    #  Helpers compartilhados
    # ─────────────────────────────────────────────────────────────────────────

    def _multi_classe_layout(self, btn_label: str, btn_callback):
        sv = ScrollView()
        lay = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(8),
        )
        lay.bind(minimum_height=lay.setter("height"))

        champ = MDTextField(
            hint_text="Campeao",
            size_hint_y=None,
            height=dp(48),
        )
        lay.add_widget(champ)

        lay.add_widget(MDLabel(
            text="Minimo de cada classe na composicao inimiga:",
            font_style="Caption",
            size_hint_y=None,
            height=dp(22),
        ))

        fields = {}
        for cl in CLASSES:
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(52),
                spacing=dp(8),
            )
            lbl = MDLabel(
                text=f"{cl}:",
                size_hint_x=0.45,
                halign="left",
                valign="middle",
            )
            f = IntField(min_val=0, max_val=5, value=0, size_hint_x=0.55)
            fields[cl] = f
            row.add_widget(lbl)
            row.add_widget(f)
            lay.add_widget(row)

        lay.add_widget(MDRaisedButton(
            text=btn_label,
            size_hint_y=None,
            height=dp(48),
            on_release=btn_callback,
        ))

        out = LogOutput(size_hint_y=None, height=dp(340))
        lay.add_widget(out)

        sv.add_widget(lay)
        return sv, champ, fields, out

    def _capture(self, func, *args, **kwargs) -> str:
        old = sys.stdout
        buf = io.StringIO()
        sys.stdout = buf
        try:
            func(*args, **kwargs)
            return buf.getvalue()
        except Exception as e:
            return f"Erro: {e}\n"
        finally:
            sys.stdout = old

    def _run_thread(self, worker, status_msg: str):
        self.status_lbl.text = f"Aguarde: {status_msg}"
        threading.Thread(target=worker, daemon=True).start()

    def _done(self):
        Clock.schedule_once(
            lambda dt: setattr(self.status_lbl, "text", "Concluido."), 0
        )

    @staticmethod
    def _ler_comp(fields: dict) -> dict:
        return {cl: f.get() for cl, f in fields.items() if f.get() > 0}


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ILoLApp().run()
