import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
import json
from typing import Dict, Any, List

from herramientas_semanticas import cargar_red_simplificada, guardar_red_simplificada
from recomendador import recomendar_platillos_bn

DATA_DIR = Path(__file__).parent / 'data'
SN_PATH = DATA_DIR / 'red_semantica.json'
DISHES_PATH = DATA_DIR / 'platillos.json'
ING_DISP_PATH = DATA_DIR / 'ingredientes_disponibilidad.json'

# Presets de restricciones adaptados al menú italiano actual.
# Al aplicar un preset, sus ingredientes se añaden a `restricciones` del usuario.
PRESETS = {
    'Vegano': [
        'carne molida', 'salsa boloñesa', 'mozzarella', 'queso parmesano', 'mascarpone',
        'bechamel', 'huevo'
    ],
    'Vegetariano': [
        'carne molida', 'salsa boloñesa'
    ],
    'Sin gluten': [
        'masa', 'pan', 'láminas de pasta', 'spaghetti'
    ],
    'Sin lactosa': [
        'mozzarella', 'queso parmesano', 'mascarpone', 'bechamel'
    ],
    'Sin huevo': [
        'huevo'
    ]
}

# Configuración visual global de la UI (fuentes, paddings, tamaños)
UI = {
    'font_large': ('TkDefaultFont', 14),
    'font_med': ('TkDefaultFont', 12),
    'padx': 8,
    'pady': 8,
    'btn_width': 18,
    'list_height': 12,
}


class RecommenderGUI:
    def __init__(self, root: tk.Tk):
        # Guardar referencia a la raíz y ajustar tamaño inicial
        self.root = root
        self.root.title('Recomendador de Platillos')
        # Empezamos con una ventana compacta para el login y la centramos
        # Esto evita mucho espacio vacío en la pantalla de login.
        self.root.resizable(False, False)
        self._center_window(self.root, 520, 260)
        self.red = cargar_red_simplificada(str(SN_PATH)) if SN_PATH.exists() else {'usuarios': {}}
        self.platillos = self._load_json(DISHES_PATH)
        self.disponibilidad = self._load_json(ING_DISP_PATH)
        self.usuario_id = None

        self._build_login()

    def _load_json(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _center_window(self, win: tk.Toplevel | tk.Tk, width: int, height: int):
        """Centra la ventana `win` en la pantalla con el tamaño dado."""
        win.update_idletasks()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = int((screen_w - width) / 2)
        y = int((screen_h - height) / 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def _build_login(self):
        # Limpiar la ventana y crear un formulario compacto y centrado
        for w in self.root.winfo_children():
            w.destroy()

        frm = tk.Frame(self.root, padx=UI['padx']*2, pady=UI['pady']*2)
        # Colocar el frame exactamente en el centro de la ventana
        frm.place(relx=0.5, rely=0.5, anchor='center')

        
        tk.Label(frm, text='Nombre de usuario:', font=UI['font_med']).grid(row=0, column=0, sticky='e', padx=(0,8))
        self.entry_user = tk.Entry(frm, font=UI['font_med'], width=28)
        self.entry_user.grid(row=0, column=1, sticky='w')
        tk.Button(frm, text='Entrar', font=UI['font_med'], width=14, command=self._on_login).grid(row=1, column=0, columnspan=2, pady=10)

        
        self.entry_user.focus_set()

    def _on_login(self):
        nombre = self.entry_user.get().strip()
        if not nombre:
            messagebox.showwarning('Usuario', 'Introduce un nombre')
            return
        uid = nombre
        # crear en la red si no existe
        self.red.setdefault('usuarios', {})
        if uid not in self.red['usuarios']:
            self.red['usuarios'][uid] = {
                'platos_gustan': [],
                'platos_no_gustan': [],
                'ingredientes_gustan': [],
                'alergias': [],
                'restricciones': [],
                'ingredientes_no_gustan': []
            }
        self.usuario_id = uid
        
        self.root.resizable(True, True)
        self._center_window(self.root, 900, 600)
        self._build_main()

    def _build_main(self):
        for w in self.root.winfo_children():
            w.destroy()
        
        frm = tk.Frame(self.root, padx=UI['padx'], pady=UI['pady'])
        frm.pack(fill='both', expand=True)
        frm.columnconfigure(0, weight=3)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(0, weight=0)
        frm.rowconfigure(1, weight=1)
        tk.Label(frm, text=f'Usuario: {self.usuario_id}', font=UI['font_large']).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,6))

       
        left = tk.Frame(frm)
        left.grid(row=1, column=0, sticky='nsew')
        
        side_panel = tk.Frame(frm, padx=10)
        side_panel.grid(row=1, column=1, sticky='nsew')
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        
        list_frame = tk.Frame(left)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0,8))
        self.plat_listbox = tk.Listbox(list_frame, height=UI['list_height'], font=UI['font_med'])
        self.plat_listbox.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(list_frame, command=self.plat_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.plat_listbox.config(yscrollcommand=scrollbar.set)

        
        btns = tk.Frame(left)
        btns.grid(row=0, column=1, sticky='n', padx=(0,4))
        tk.Button(btns, text='Me gusta', font=UI['font_med'], width=UI['btn_width'], command=self._mark_gusta).pack(pady=4)
        tk.Button(btns, text='No me gusta', font=UI['font_med'], width=UI['btn_width'], command=self._mark_no_gusta).pack(pady=4)
        tk.Button(btns, text='Neutral', font=UI['font_med'], width=UI['btn_width'], command=self._mark_neutral).pack(pady=4)

        for p in self.platillos:
            self.plat_listbox.insert('end', f"{p['id']} - {p.get('name','')}")

        # Panel lateral para mostrar restricciones, alergias, gustos y no gustos
        tk.Label(side_panel, text='Restricciones activas:', font=UI['font_med']).pack(anchor='w')
        self.lbl_restr = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_restr.pack(anchor='w', pady=4)
        tk.Label(side_panel, text='Alergias activas:', font=UI['font_med']).pack(anchor='w', pady=(8,0))
        self.lbl_alerg = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_alerg.pack(anchor='w', pady=4)

        # Gustos / No gustos de platos
        tk.Label(side_panel, text='Platos que te gustan:', font=UI['font_med']).pack(anchor='w', pady=(10,0))
        self.lbl_platos_gustan = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_platos_gustan.pack(anchor='w', pady=2)
        tk.Label(side_panel, text='Platos que no te gustan:', font=UI['font_med']).pack(anchor='w', pady=(6,0))
        self.lbl_platos_no_gustan = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_platos_no_gustan.pack(anchor='w', pady=2)

        # Gustos / No gustos de ingredientes
        tk.Label(side_panel, text='Ingredientes que te gustan:', font=UI['font_med']).pack(anchor='w', pady=(10,0))
        self.lbl_ings_gustan = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_ings_gustan.pack(anchor='w', pady=2)
        tk.Label(side_panel, text='Ingredientes que no te gustan:', font=UI['font_med']).pack(anchor='w', pady=(6,0))
        self.lbl_ings_no_gustan = tk.Label(side_panel, text='', font=UI['font_med'], wraplength=220, justify='left')
        self.lbl_ings_no_gustan.pack(anchor='w', pady=2)

        self._update_side_panel()

        # Botones inferiores centrados y con spacing uniforme
        bottom = tk.Frame(frm)
        bottom.grid(row=2, column=0, columnspan=2, pady=12)
        tk.Button(bottom, text='Ingredientes (Gusta/No)', font=UI['font_med'], width=18, command=self._open_ingredientes).pack(side='left', padx=6)
        tk.Button(bottom, text='Restricciones / Alergias', font=UI['font_med'], width=20, command=self._open_restricciones).pack(side='left', padx=6)
        tk.Button(bottom, text='Presets (veg/alu/...)', font=UI['font_med'], width=20, command=self._open_presets).pack(side='left', padx=6)
        tk.Button(bottom, text='Ver recomendaciones', font=UI['font_med'], width=20, command=self._ver_recomendaciones).pack(side='left', padx=6)
        tk.Button(bottom, text='Guardar y salir', font=UI['font_med'], width=18, command=self._guardar_y_salir).pack(side='left', padx=6)

    def _current_usuario(self) -> Dict[str, Any]:
        return self.red['usuarios'][self.usuario_id]

    def _update_side_panel(self):
        """Actualiza los labels laterales que muestran restricciones y alergias.

        Llamar a esta función cada vez que se modifiquen `restricciones` o `alergias`.
        """
        # Si no hay usuario logueado, limpiar todos los labels del panel lateral
        if not self.usuario_id:
            for lbl in ('lbl_restr', 'lbl_alerg', 'lbl_platos_gustan', 'lbl_platos_no_gustan', 'lbl_ings_gustan', 'lbl_ings_no_gustan'):
                if hasattr(self, lbl):
                    getattr(self, lbl).config(text='')
            return

        u = self._current_usuario()
        restr = u.get('restricciones', []) or []
        alerg = u.get('alergias', []) or []
        platos_g = u.get('platos_gustan', []) or []
        platos_ng = u.get('platos_no_gustan', []) or []
        ings_g = u.get('ingredientes_gustan', []) or []
        ings_ng = u.get('ingredientes_no_gustan', []) or []

        # Mostrar restricciones y alergias
        self.lbl_restr.config(text=', '.join(restr) if restr else '(ninguna)')
        self.lbl_alerg.config(text=', '.join(alerg) if alerg else '(ninguna)')

        # Mapa id->nombre para mostrar nombres legibles de platos
        id2name = {p['id']: p.get('name', '') for p in self.platillos}

        def _format_platos_list(plist):
            if not plist:
                return '(ninguno)'
            items = []
            for pid in plist:
                name = id2name.get(pid, '')
                items.append(f"{pid} - {name}" if name else pid)
            return ', '.join(items)

        self.lbl_platos_gustan.config(text=_format_platos_list(platos_g))
        self.lbl_platos_no_gustan.config(text=_format_platos_list(platos_ng))

        # Ingredientes
        self.lbl_ings_gustan.config(text=', '.join(ings_g) if ings_g else '(ninguno)')
        self.lbl_ings_no_gustan.config(text=', '.join(ings_ng) if ings_ng else '(ninguno)')

    def _mark_gusta(self):
        sel = self.plat_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        pid = self.platillos[idx]['id']
        u = self._current_usuario()
        if pid in u.get('platos_no_gustan', []):
            u['platos_no_gustan'].remove(pid)
        if pid not in u.get('platos_gustan', []):
            u['platos_gustan'].append(pid)
        messagebox.showinfo('OK', 'Marcado como gusta')
        self._update_side_panel()

    def _mark_no_gusta(self):
        sel = self.plat_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        pid = self.platillos[idx]['id']
        u = self._current_usuario()
        if pid in u.get('platos_gustan', []):
            u['platos_gustan'].remove(pid)
        if pid not in u.get('platos_no_gustan', []):
            u['platos_no_gustan'].append(pid)
        messagebox.showinfo('OK', 'Marcado como no gusta')
        self._update_side_panel()

    def _mark_neutral(self):
        sel = self.plat_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        pid = self.platillos[idx]['id']
        u = self._current_usuario()
        if pid in u.get('platos_gustan', []):
            u['platos_gustan'].remove(pid)
        if pid in u.get('platos_no_gustan', []):
            u['platos_no_gustan'].remove(pid)
        messagebox.showinfo('OK', 'Marcado como neutral')
        self._update_side_panel()

    def _open_ingredientes(self):
        # Ventana para gestionar ingredientes (like/dislike)
        win = tk.Toplevel(self.root)
        win.title('Ingredientes')
        self._center_window(win, 420, 400)
        list_frame = tk.Frame(win)
        list_frame.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        lst = tk.Listbox(list_frame, height=UI['list_height'], font=UI['font_med'])
        lst.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(list_frame, command=lst.yview)
        scrollbar.pack(side='right', fill='y')
        lst.config(yscrollcommand=scrollbar.set)
        for ing in sorted({ing.lower() for p in self.platillos for ing in p.get('ingredients', [])}):
            lst.insert('end', ing)
        btns = tk.Frame(win)
        btns.pack(side='left', padx=8, pady=8)
        tk.Button(btns, text='Me gusta', font=UI['font_med'], width=14, command=lambda: self._mark_ingred(lst, True)).pack(pady=6)
        tk.Button(btns, text='No me gusta', font=UI['font_med'], width=14, command=lambda: self._mark_ingred(lst, False)).pack(pady=6)
        tk.Button(btns, text='Neutral', font=UI['font_med'], width=14, command=lambda: self._mark_ingred_neutral(lst)).pack(pady=6)

    def _mark_ingred(self, listbox: tk.Listbox, like: bool):
        sel = listbox.curselection()
        if not sel:
            return
        ing = listbox.get(sel[0])
        u = self._current_usuario()
        if like:
            if ing in u.get('ingredientes_no_gustan', []):
                u['ingredientes_no_gustan'].remove(ing)
            if ing not in u.get('ingredientes_gustan', []):
                u['ingredientes_gustan'].append(ing)
            messagebox.showinfo('OK', f'{ing} marcado como gusta')
            self._update_side_panel()
        else:
            if ing in u.get('ingredientes_gustan', []):
                u['ingredientes_gustan'].remove(ing)
            if ing not in u.get('ingredientes_no_gustan', []):
                u['ingredientes_no_gustan'].append(ing)
            messagebox.showinfo('OK', f'{ing} marcado como no gusta')
            self._update_side_panel()

    def _mark_ingred_neutral(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        ing = listbox.get(sel[0])
        u = self._current_usuario()
        if ing in u.get('ingredientes_gustan', []):
            u['ingredientes_gustan'].remove(ing)
        if ing in u.get('ingredientes_no_gustan', []):
            u['ingredientes_no_gustan'].remove(ing)
        messagebox.showinfo('OK', f'{ing} marcado como neutral')
        self._update_side_panel()

    def _open_restricciones(self):
        # Ventana para ver y editar restricciones y alergias
        win = tk.Toplevel(self.root)
        win.title('Restricciones / Alergias')
        self._center_window(win, 520, 420)
        list_frame = tk.Frame(win)
        list_frame.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        lst = tk.Listbox(list_frame, height=UI['list_height'], font=UI['font_med'])
        lst.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(list_frame, command=lst.yview)
        scrollbar.pack(side='right', fill='y')
        lst.config(yscrollcommand=scrollbar.set)
        options = sorted({ing.lower() for p in self.platillos for ing in p.get('ingredients', [])})
        for opt in options:
            lst.insert('end', opt)
        btns = tk.Frame(win)
        btns.pack(side='left', padx=8, pady=8)
        tk.Button(btns, text='Toggle Alergia', font=UI['font_med'], width=16, command=lambda: self._toggle_alergia(lst)).pack(pady=6)
        tk.Button(btns, text='Toggle Restricción', font=UI['font_med'], width=16, command=lambda: self._toggle_restriccion(lst)).pack(pady=6)

    def _open_presets(self):
        # Ventana de presets (igual que antes, pero con fuente más grande)
        win = tk.Toplevel(self.root)
        win.title('Presets de restricciones')
        self._center_window(win, 420, 300)
        lst = tk.Listbox(win, height=8, font=UI['font_med'])
        lst.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        for name in PRESETS.keys():
            lst.insert('end', name)
        btns = tk.Frame(win)
        btns.pack(side='left', padx=8, pady=8)
        tk.Button(btns, text='Aplicar preset', font=UI['font_med'], width=16, command=lambda: self._apply_selected_preset(lst)).pack(pady=6)
        tk.Button(btns, text='Quitar preset', font=UI['font_med'], width=16, command=lambda: self._remove_selected_preset(lst)).pack(pady=6)
        tk.Button(btns, text='Ver ingredientes del preset', font=UI['font_med'], width=16, command=lambda: self._show_preset_ingredients(lst)).pack(pady=6)

    def _apply_selected_preset(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        name = listbox.get(sel[0])
        self._apply_preset(name)

    def _remove_selected_preset(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        name = listbox.get(sel[0])
        self._remove_preset(name)

    def _show_preset_ingredients(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        name = listbox.get(sel[0])
        ings = PRESETS.get(name, [])
        messagebox.showinfo(name, 'Ingredientes en el preset:\n' + ', '.join(sorted(set(ings))))

    def _apply_preset(self, name: str):
        u = self._current_usuario()
        preset_ings = PRESETS.get(name, [])
        # normalizar a lowercase
        preset_ings = [i.lower() for i in preset_ings]
        added = []
        for ing in preset_ings:
            # quitar de ingredientes que gustan si hubiera conflicto
            if ing in u.get('ingredientes_gustan', []):
                u['ingredientes_gustan'].remove(ing)
            if ing not in u.get('restricciones', []):
                u.setdefault('restricciones', []).append(ing)
                added.append(ing)
        if added:
            messagebox.showinfo('Preset aplicado', f"Se añadieron a restricciones: {', '.join(added)}")
        else:
            messagebox.showinfo('Preset', 'No había cambios (ya aplicado)')
        self._update_side_panel()

    def _remove_preset(self, name: str):
        u = self._current_usuario()
        preset_ings = PRESETS.get(name, [])
        preset_ings = [i.lower() for i in preset_ings]
        removed = []
        for ing in preset_ings:
            if ing in u.get('restricciones', []):
                u['restricciones'].remove(ing)
                removed.append(ing)
        if removed:
            messagebox.showinfo('Preset removido', f"Se quitaron de restricciones: {', '.join(removed)}")
        else:
            messagebox.showinfo('Preset', 'No había elementos del preset en las restricciones')
        self._update_side_panel()

    def _toggle_alergia(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        ing = listbox.get(sel[0])
        u = self._current_usuario()
        if ing in u.get('alergias', []):
            u['alergias'].remove(ing)
            messagebox.showinfo('OK', f'{ing} removida de alergias')
        else:
            u['alergias'].append(ing)
            messagebox.showinfo('OK', f'{ing} añadida a alergias')
        self._update_side_panel()

    def _toggle_restriccion(self, listbox: tk.Listbox):
        sel = listbox.curselection()
        if not sel:
            return
        ing = listbox.get(sel[0])
        u = self._current_usuario()
        if ing in u.get('restricciones', []):
            u['restricciones'].remove(ing)
            messagebox.showinfo('OK', f'{ing} removida de restricciones')
        else:
            u['restricciones'].append(ing)
            messagebox.showinfo('OK', f'{ing} añadida a restricciones')
        self._update_side_panel()

    def _ver_recomendaciones(self):
        try:
            u = self._current_usuario()
            recs = recomendar_platillos_bn(self.platillos, u, disponibilidad_ingredientes=self.disponibilidad, normalize=True)
        except Exception as e:
            messagebox.showerror('Error', f'Error al calcular recomendaciones: {e}')
            return
        win = tk.Toplevel(self.root)
        win.title('Recomendaciones')
        txt = tk.Text(win, width=80, height=20)
        txt.pack()
        for p in recs:
            txt.insert('end', f"[{p['id']}] {p.get('name','')} - P={p.get('probability',0):.2f}\n")

    def _guardar_y_salir(self):
        guardar_red_simplificada(str(SN_PATH), self.red)
        messagebox.showinfo('Guardado', 'Red semántica guardada. Saliendo...')
        self.root.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = RecommenderGUI(root)
    root.mainloop()
