import customtkinter as ctk
from .styles import COLORS, SIDEBAR_W
from .layout import Sidebar
from .pantalla_principal import PantallaPrincipal
from .vista_paciente import VistaPaciente
from .form_paciente import FormPaciente
from .form_consulta import FormConsulta
from .config import PantallaConfig
from .ficha_clinica import FichaClinica
from .calendario import PantallaCalendario
from .dialogo_backup import DialogoBackup

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Historial Clínico")
        self.geometry("1140x740")
        self.minsize(960, 620)
        self.configure(fg_color=COLORS["sidebar"])
        self._build()
        self.navigate("principal", None)

    def _build(self):
        root = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], corner_radius=0)
        root.pack(fill="both", expand=True)

        self._sidebar = Sidebar(root, nav=self.navigate, on_backup=self._abrir_backup)
        self._sidebar.pack(side="left", fill="y")

        # Línea divisora
        ctk.CTkFrame(root, width=1, fg_color=COLORS["sidebar_border"],
                     corner_radius=0).pack(side="left", fill="y")

        self._content = ctk.CTkFrame(root, fg_color=COLORS["bg"], corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

        self._screens = {
            "principal":      PantallaPrincipal(self._content, self.navigate),
            "vista_paciente": VistaPaciente(self._content, self.navigate),
            "form_paciente":  FormPaciente(self._content, self.navigate),
            "form_consulta":  FormConsulta(self._content, self.navigate),
            "config":         PantallaConfig(self._content, self.navigate),
            "ficha_clinica":  FichaClinica(self._content, self.navigate),
            "calendario":     PantallaCalendario(self._content, self.navigate),
        }
        for s in self._screens.values():
            s.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._current = None

    def navigate(self, screen: str, data):
        target = self._screens[screen]
        old    = self._current

        self._sidebar.set_active(screen)

        if hasattr(target, "on_show"):
            target.on_show(data)

        if old is None or old is target:
            target.lift()
            target.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._current = target
            return

        self._current = target
        from .animations import slide_screens
        slide_screens(old, target)

    def _abrir_backup(self):
        on_restore = getattr(self._screens.get("principal"), "on_show", None)
        DialogoBackup(self, on_restauracion=lambda: on_restore(None) if on_restore else None)

    def toast(self, message: str, kind: str = "success"):
        from .widgets import Toast
        Toast(self, message, kind)
