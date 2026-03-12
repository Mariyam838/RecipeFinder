"""
recipe_vault.py  ──  The Recipe Vault Desktop App
══════════════════════════════════════════════════
Sections: Name · Ingredient · Category · Area · Random
Aesthetic: Midnight Spice Market (see theme.py)

Install:  pip install requests pillow
Run:      python recipe_vault.py
"""

import tkinter as tk
from tkinter import font as tkfont
import requests
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from io import BytesIO
import threading
import webbrowser

from theme import C, F, S, WS, TS, TAB_ACCENT, Deco

API = "https://www.themealdb.com/api/json/v1/1"


# ══════════════════════════════════════════════════════════════════════════════
#  API
# ══════════════════════════════════════════════════════════════════════════════
class MealAPI:
    @staticmethod
    def _get(ep, params=None):
        try:
            r = requests.get(f"{API}{ep}", params=params, timeout=9)
            return r.json()
        except Exception:
            return {}

    @classmethod
    def search_name(cls, q):
        """Search meals by name. Tries exact query first, then first word only."""
        results = cls._get("/search.php", {"s": q}).get("meals") or []
        # If nothing found and query has multiple words, try first significant word
        if not results and " " in q:
            first_word = q.split()[0]
            if len(first_word) > 2:
                results = cls._get("/search.php", {"s": first_word}).get("meals") or []
        return results
    @classmethod
    def search_ing(cls, i):        return cls._get("/filter.php",  {"i": i}).get("meals") or []
    @classmethod
    def filter_cat(cls, c):        return cls._get("/filter.php",  {"c": c}).get("meals") or []
    @classmethod
    def filter_area(cls, a):       return cls._get("/filter.php",  {"a": a}).get("meals") or []
    @classmethod
    def lookup(cls, mid):
        m = cls._get("/lookup.php", {"i": mid}).get("meals")
        return m[0] if m else None
    @classmethod
    def random(cls):
        m = cls._get("/random.php").get("meals")
        return m[0] if m else None

    @staticmethod
    def fetch_img(url, size):
        """Fetch and resize a meal image from TheMealDB."""
        # MealDB stores images as plain .jpg URLs — just fetch them directly.
        # No /preview suffix needed; that path is not a real image endpoint.
        clean_url = url.strip().rstrip("/")

        # Some older MealDB entries use http — upgrade to https
        if clean_url.startswith("http://"):
            clean_url = "https://" + clean_url[7:]

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/jpeg,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.themealdb.com/",
        }

        session = requests.Session()
        session.headers.update(headers)

        try:
            r = session.get(clean_url, timeout=15)
            if r.status_code == 200 and len(r.content) > 1000:
                img = Image.open(BytesIO(r.content)).convert("RGB")
                img = img.resize(size, Image.LANCZOS)
                return img
        except Exception:
            pass

        return None

    @staticmethod
    def ingredients(meal):
        out = []
        for i in range(1, 21):
            n = (meal.get(f"strIngredient{i}") or "").strip()
            q = (meal.get(f"strMeasure{i}")    or "").strip()
            if n:
                out.append((n, q))
        return out


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def hdiv(parent, color=C.DIVIDER, h=1, px=0, py=0):
    """Horizontal divider line."""
    tk.Frame(parent, bg=color, height=h).pack(fill="x", padx=px, pady=py)


def vdiv(parent, color=C.DIVIDER, w=1):
    """Vertical divider line."""
    tk.Frame(parent, bg=color, width=w).pack(side="left", fill="y")


class HoverButton(tk.Label):
    """Label styled as a hover-animated button."""
    def __init__(self, parent, text, command=None,
                 bg=C.BG3, fg=C.T_WARM,
                 hbg=C.BG4, hfg=C.GOLD,
                 abg=C.BG5, afg=C.GOLD,
                 font=F.SMALL, padx=10, pady=5, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=font, cursor="hand2",
                         relief="flat",
                         highlightthickness=1,
                         highlightbackground=C.B_HARD,
                         padx=padx, pady=pady, **kw)
        self._bg, self._fg   = bg, fg
        self._hbg, self._hfg = hbg, hfg
        self._abg, self._afg = abg, afg
        self._cmd = command
        self._active_state = False
        self.bind("<Enter>",    self._enter)
        self.bind("<Leave>",    self._leave)
        self.bind("<Button-1>", self._click)

    def _enter(self, _):
        if not self._active_state:
            self.configure(bg=self._hbg, fg=self._hfg,
                           highlightbackground=C.GOLD_DIM)

    def _leave(self, _):
        if not self._active_state:
            self.configure(bg=self._bg, fg=self._fg,
                           highlightbackground=C.B_HARD)

    def _click(self, _):
        if self._cmd:
            self._cmd()

    def set_active(self, on: bool):
        self._active_state = on
        if on:
            self.configure(bg=self._abg, fg=self._afg,
                           highlightbackground=C.GOLD_DEEP)
        else:
            self.configure(bg=self._bg, fg=self._fg,
                           highlightbackground=C.B_HARD)


class ScrollFrame(tk.Frame):
    """Vertically scrollable inner frame with full mouse-wheel support."""
    def __init__(self, parent, bg=C.BG1, **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical",
                          command=self.canvas.yview, **WS.SCROLLBAR)
        sb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=sb.set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._cw   = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._cw, width=e.width))
        # Bind scroll on canvas itself
        self._bind_scroll(self.canvas)
        self._bind_scroll(self.inner)

    def _do_scroll(self, e):
        # Windows / macOS: delta; Linux: Button-4 / Button-5
        if e.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif e.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1 * (e.delta // 120), "units")

    def _bind_scroll(self, widget):
        """Bind scroll events to a widget AND all its descendants."""
        widget.bind("<MouseWheel>", self._do_scroll, add="+")
        widget.bind("<Button-4>",   self._do_scroll, add="+")   # Linux scroll up
        widget.bind("<Button-5>",   self._do_scroll, add="+")   # Linux scroll down

    def bind_scroll_recursive(self, widget=None):
        """Call after adding children so scroll works everywhere."""
        target = widget or self.inner
        self._bind_scroll(target)
        for child in target.winfo_children():
            self.bind_scroll_recursive(child)

    def top(self):
        self.canvas.yview_moveto(0)

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DETAIL PANEL (right side)
# ══════════════════════════════════════════════════════════════════════════════
class DetailPanel(ScrollFrame):
    def __init__(self, parent):
        super().__init__(parent, bg=C.BG1)
        self._refs = []
        self._welcome()

    # ── Welcome screen ──────────────────────────────────────────────────────
    def _welcome(self):
        self.clear(); self._refs.clear()
        f = tk.Frame(self.inner, bg=C.BG1)
        f.pack(expand=True, pady=120, padx=40)

        # Decorative ornament
        tk.Label(f, text="✦  ✦  ✦", font=(F.SERIF, 14),
                 bg=C.BG1, fg=C.GOLD_DIM).pack(pady=(0, 16))

        tk.Label(f, text="The Recipe Vault",
                 font=(F.SERIF, 26, "bold"),
                 bg=C.BG1, fg=C.T_CREAM).pack()

        tk.Label(f, text="A Culinary Collection",
                 font=(F.SERIF, 13, "normal"),
                 bg=C.BG1, fg=C.GOLD).pack(pady=(4, 24))

        hdiv(f, C.GOLD_DIM, h=1)

        tk.Label(f,
                 text="\nChoose a section from the left panel\nto begin exploring world cuisines\n",
                 font=F.SMALL, bg=C.BG1, fg=C.T_MUTED,
                 justify="center").pack()

        # Bottom ornament
        tk.Label(f, text="✦  ✦  ✦", font=(F.SERIF, 14),
                 bg=C.BG1, fg=C.GOLD_DIM).pack(pady=(16, 0))

    # ── Loading state ────────────────────────────────────────────────────────
    def show_loading(self):
        self.clear(); self._refs.clear()
        f = tk.Frame(self.inner, bg=C.BG1)
        f.pack(expand=True, pady=100)
        tk.Label(f, text="◌", font=(F.SERIF, 42),
                 bg=C.BG1, fg=C.GOLD_DIM).pack()
        tk.Label(f, text="Loading…",
                 font=F.SMALL, bg=C.BG1, fg=C.T_MUTED).pack(pady=8)
        self.after(50, lambda: self.bind_scroll_recursive())

    # ── Empty state ──────────────────────────────────────────────────────────
    def show_empty(self, msg="No recipes found."):
        self.clear(); self._refs.clear()
        f = tk.Frame(self.inner, bg=C.BG1)
        f.pack(expand=True, pady=100)
        tk.Label(f, text="○", font=(F.SERIF, 42),
                 bg=C.BG1, fg=C.ROSE_DEEP).pack()
        tk.Label(f, text=msg, font=(F.SERIF, 13, "bold"),
                 bg=C.BG1, fg=C.T_CREAM).pack(pady=(8, 4))
        tk.Label(f, text="Try a different search",
                 font=F.SMALL, bg=C.BG1, fg=C.T_MUTED).pack()
        self.after(50, lambda: self.bind_scroll_recursive())

    # ── Full recipe render ────────────────────────────────────────────────────
    def render(self, meal):
        self.clear(); self._refs.clear()

        # ── HERO IMAGE ──────────────────────────────────────────────────────
        hero_wrap = tk.Frame(self.inner, bg=C.BG0, height=260)
        hero_wrap.pack(fill="x")
        hero_wrap.pack_propagate(False)

        self._hero_lbl = tk.Label(hero_wrap, bg=C.BG0,
                                  text="🍽  Loading image…",
                                  font=(F.SERIF, 11),
                                  fg=C.T_GHOST)
        self._hero_lbl.pack(fill="both", expand=True)

        threading.Thread(
            target=self._load_hero,
            args=(meal["strMealThumb"],),
            daemon=True
        ).start()

        # ── TITLE AREA ──────────────────────────────────────────────────────
        # Gold accent line
        tk.Frame(self.inner, bg=C.GOLD, height=3).pack(fill="x")

        title_bg = tk.Frame(self.inner, bg=C.BG2)
        title_bg.pack(fill="x")

        title_inner = tk.Frame(title_bg, bg=C.BG2)
        title_inner.pack(fill="x", padx=S.LG, pady=(S.MD, S.SM))

        # Category + area badges
        badge_row = tk.Frame(title_inner, bg=C.BG2)
        badge_row.pack(fill="x", anchor="w", pady=(0, 6))

        if meal.get("strCategory"):
            tk.Label(badge_row,
                     text=f"  {meal['strCategory'].upper()}  ",
                     font=F.LABEL, bg=C.GOLD_DIM, fg=C.GOLD,
                     padx=6, pady=3
                     ).pack(side="left", padx=(0, 6))

        if meal.get("strArea"):
            tk.Label(badge_row,
                     text=f"  {meal['strArea']}  ",
                     font=F.LABEL, bg=C.VIOLET_D, fg=C.VIOLET_L,
                     padx=6, pady=3
                     ).pack(side="left", padx=(0, 6))

        # Tags
        if meal.get("strTags"):
            for tag in meal["strTags"].split(","):
                t = tag.strip()
                if t:
                    tk.Label(badge_row, text=f"#{t}",
                             font=F.LABEL, bg=C.BG3, fg=C.T_MUTED,
                             padx=5, pady=3
                             ).pack(side="left", padx=(0, 4))

        # Recipe name
        tk.Label(title_inner, text=meal["strMeal"],
                 font=(F.SERIF, 20, "bold"),
                 bg=C.BG2, fg=C.T_CREAM,
                 anchor="w", wraplength=700, justify="left"
                 ).pack(fill="x")

        hdiv(self.inner, C.DIVIDER)

        # ── TWO-COLUMN BODY ──────────────────────────────────────────────────
        cols = tk.Frame(self.inner, bg=C.BG1)
        cols.pack(fill="both", expand=True)

        # LEFT: Ingredients
        ing_col = tk.Frame(cols, bg=C.BG2, width=240)
        ing_col.pack(side="left", fill="y")
        ing_col.pack_propagate(False)

        # Ingredients header
        ing_hdr = tk.Frame(ing_col, bg=C.BG3)
        ing_hdr.pack(fill="x")
        tk.Frame(ing_hdr, bg=C.SAGE, height=2).pack(fill="x")
        tk.Label(ing_hdr, text="🌿  INGREDIENTS",
                 font=F.MICRO_B, bg=C.BG3, fg=C.SAGE_LIGHT,
                 pady=8, padx=12, anchor="w"
                 ).pack(fill="x")
        hdiv(ing_col, C.DIVIDER)

        ings = MealAPI.ingredients(meal)
        for idx, (name, qty) in enumerate(ings):
            row_bg = C.BG2 if idx % 2 == 0 else C.BG3
            row = tk.Frame(ing_col, bg=row_bg)
            row.pack(fill="x")
            # Bullet dot
            tk.Label(row, text="·", font=(F.SERIF, 14),
                     bg=row_bg, fg=C.GOLD_DIM,
                     width=2).pack(side="left", pady=4)
            tk.Label(row, text=name,
                     font=F.SMALL, bg=row_bg, fg=C.T_WARM,
                     anchor="w", pady=5
                     ).pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"{qty}  ",
                     font=F.SMALL_B, bg=row_bg, fg=C.GOLD,
                     anchor="e"
                     ).pack(side="right")

        # Count badge at bottom
        tk.Label(ing_col,
                 text=f"{len(ings)} ingredients",
                 font=F.LABEL, bg=C.BG3, fg=C.T_GHOST,
                 pady=6).pack(fill="x", side="bottom")

        # Separator
        vdiv(cols, C.DIVIDER)

        # RIGHT: Instructions
        inst_col = tk.Frame(cols, bg=C.BG2)
        inst_col.pack(side="left", fill="both", expand=True)

        inst_hdr = tk.Frame(inst_col, bg=C.BG3)
        inst_hdr.pack(fill="x")
        tk.Frame(inst_hdr, bg=C.GOLD, height=2).pack(fill="x")
        tk.Label(inst_hdr, text="📋  INSTRUCTIONS",
                 font=F.MICRO_B, bg=C.BG3, fg=C.GOLD_LIGHT,
                 pady=8, padx=12, anchor="w"
                 ).pack(fill="x")
        hdiv(inst_col, C.DIVIDER)

        raw   = meal.get("strInstructions", "").strip()
        steps = [p.strip() for p in raw.split("\n") if p.strip()]

        inst_body = tk.Frame(inst_col, bg=C.BG2)
        inst_body.pack(fill="both", expand=True, padx=14, pady=12)

        for i, step in enumerate(steps, 1):
            srow = tk.Frame(inst_body, bg=C.BG2)
            srow.pack(fill="x", anchor="w", pady=(0, 10))

            # Numbered bubble
            bubble = tk.Label(srow, text=str(i),
                              font=F.SMALL_B,
                              bg=C.GOLD_DEEP, fg=C.T_CREAM,
                              width=3, pady=3)
            bubble.pack(side="left", anchor="nw", padx=(0, 10))

            tk.Label(srow, text=step,
                     font=F.SMALL, bg=C.BG2,
                     fg=C.T_WARM, justify="left",
                     anchor="nw", wraplength=420
                     ).pack(side="left", anchor="nw",
                            fill="x", expand=True)

        # ── FOOTER ──────────────────────────────────────────────────────────
        tk.Frame(self.inner, bg=C.GOLD_DIM, height=1).pack(fill="x")
        foot = tk.Frame(self.inner, bg=C.BG3)
        foot.pack(fill="x")

        foot_inner = tk.Frame(foot, bg=C.BG3)
        foot_inner.pack(fill="x", padx=S.LG, pady=S.SM)

        if meal.get("strArea"):
            tk.Label(foot_inner,
                     text=f"Cuisine of {meal['strArea']}",
                     font=F.MICRO, bg=C.BG3, fg=C.T_GHOST
                     ).pack(side="left")

        btn_frame = tk.Frame(foot_inner, bg=C.BG3)
        btn_frame.pack(side="right")

        if meal.get("strYoutube"):
            u = meal["strYoutube"]
            tk.Button(btn_frame, text="▶  YouTube",
                      **WS.BTN_ROSE, padx=14, pady=6,
                      command=lambda: webbrowser.open(u)
                      ).pack(side="left", padx=(0, 6))

        if meal.get("strSource"):
            u = meal["strSource"]
            tk.Button(btn_frame, text="🔗  Source",
                      **WS.BTN_GHOST, padx=12, pady=6,
                      command=lambda: webbrowser.open(u)
                      ).pack(side="left")

        # Bind mouse-wheel scroll to every widget in the detail panel
        self.after(50, lambda: self.bind_scroll_recursive())
        self.top()

    def _load_hero(self, url):
        img = MealAPI.fetch_img(url, (800, 260))
        if img:
            img = ImageEnhance.Brightness(img).enhance(0.72)
            img = ImageEnhance.Color(img).enhance(0.82)
            photo = ImageTk.PhotoImage(img)
            self._refs.append(photo)
            self.inner.after(0, lambda: self._hero_lbl.configure(
                image=photo, text="", compound="center"))
        else:
            self.inner.after(0, lambda: self._hero_lbl.configure(
                text="🍽   Image unavailable",
                font=(F.SERIF, 13),
                fg=C.T_GHOST))


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR TAB BAR
# ══════════════════════════════════════════════════════════════════════════════
class SideBar(tk.Frame):
    TABS = [
        ("🔍", "By Name",       "name"),
        ("🌿", "By Ingredient", "ingredient"),
        ("📂", "By Category",   "category"),
        ("🌍", "By Cuisine",    "area"),
        ("🎲", "Random",        "random"),
    ]

    def __init__(self, parent, on_change):
        super().__init__(parent, bg=C.BG2, width=170)
        self.pack_propagate(False)
        self._on_change = on_change
        self._btns = {}
        self._active = None
        self._build()

    def _build(self):
        # Logo
        logo = tk.Frame(self, bg=C.BG0, height=90)
        logo.pack(fill="x")
        logo.pack_propagate(False)

        tk.Label(logo, text="🍽",
                 font=(F.SERIF, 30),
                 bg=C.BG0, fg=C.GOLD).pack(pady=(16, 0))
        tk.Label(logo, text="RECIPE VAULT",
                 font=F.LABEL,
                 bg=C.BG0, fg=C.T_GHOST).pack()

        tk.Frame(self, bg=C.GOLD_DIM, height=1).pack(fill="x")
        tk.Frame(self, bg=C.BG2, height=S.SM).pack()

        # Nav label
        tk.Label(self, text="  BROWSE",
                 font=F.LABEL, bg=C.BG2, fg=C.T_GHOST,
                 anchor="w", pady=4).pack(fill="x")

        # Tab buttons
        for icon, label, key in self.TABS:
            accent = TAB_ACCENT.get(key, C.GOLD)
            btn = tk.Button(self,
                            text=f"  {icon}  {label}",
                            **TS.INACTIVE,
                            command=lambda k=key: self.activate(k))
            btn.pack(fill="x", padx=4, pady=1)
            self._btns[key] = btn

        # Spacer
        tk.Frame(self, bg=C.BG2).pack(fill="both", expand=True)

        # Footer
        tk.Frame(self, bg=C.DIVIDER, height=1).pack(fill="x")
        tk.Label(self, text="TheMealDB  ·  Free API",
                 font=F.LABEL, bg=C.BG2, fg=C.T_GHOST,
                 pady=8).pack()

    def activate(self, key):
        if self._active:
            self._btns[self._active].configure(**TS.INACTIVE)
        kw = dict(TS.ACTIVE)
        # Coloured left border effect via bg
        self._btns[key].configure(**kw)
        self._active = key
        self._on_change(key)


# ══════════════════════════════════════════════════════════════════════════════
#  BASE TAB  (shared logic)
# ══════════════════════════════════════════════════════════════════════════════
class BaseTab(tk.Frame):
    def __init__(self, parent, detail: DetailPanel):
        super().__init__(parent, bg=C.BG1)
        self.detail = detail
        self._meals = []
        self._cache = {}
        self._build()

    def _build(self): pass

    def _thread(self, fn, cb):
        def run():
            result = fn()
            self.after(0, lambda: cb(result))
        threading.Thread(target=run, daemon=True).start()

    def _open(self, meal_id):
        self.detail.show_loading()
        if meal_id in self._cache:
            self.detail.render(self._cache[meal_id])
            return
        def fetch():
            m = MealAPI.lookup(meal_id)
            if m:
                self._cache[meal_id] = m
            return m
        def done(m):
            if m: self.detail.render(m)
            else: self.detail.show_empty("Could not load recipe.")
        self._thread(fetch, done)

    def _make_listbox(self, parent):
        """Styled listbox with scrollbar."""
        wrap = tk.Frame(parent, bg=C.BG2,
                        highlightthickness=1,
                        highlightbackground=C.B_HARD)
        wrap.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        lb = tk.Listbox(wrap, **WS.LISTBOX, cursor="hand2")
        lb.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(wrap, orient="vertical",
                          command=lb.yview, **WS.SCROLLBAR)
        sb.pack(side="right", fill="y")
        lb.configure(yscrollcommand=sb.set)
        return lb

    def _fill_list(self, lb, meals):
        lb.delete(0, "end")
        self._meals = meals
        for m in meals:
            area = f"  ·  {m['strArea']}" if m.get("strArea") else ""
            lb.insert("end", f"   {m['strMeal']}{area}")
        if meals:
            lb.selection_set(0)
            lb.event_generate("<<ListboxSelect>>")

    def _on_select(self, _, lb):
        sel = lb.curselection()
        if sel:
            self._open(self._meals[sel[0]]["idMeal"])

    # ── Tab header bar with coloured accent ──────────────────────────────────
    def _make_header(self, title, accent_color, subtitle=""):
        hdr = tk.Frame(self, bg=C.BG3)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=accent_color, height=3).pack(fill="x")
        inner = tk.Frame(hdr, bg=C.BG3)
        inner.pack(fill="x", padx=S.MD, pady=(8, 8))
        tk.Label(inner, text=title,
                 font=(F.SERIF, 13, "bold"),
                 bg=C.BG3, fg=C.T_CREAM,
                 anchor="w").pack(fill="x")
        if subtitle:
            tk.Label(inner, text=subtitle,
                     font=F.MICRO, bg=C.BG3, fg=C.T_GHOST,
                     anchor="w").pack(fill="x")
        hdiv(self, C.DIVIDER)

    # ── Search input row ────────────────────────────────────────────────────
    def _make_input(self, parent, var, placeholder,
                    btn_text, btn_cmd, btn_style=None):
        row = tk.Frame(parent, bg=C.BG1)
        row.pack(fill="x", padx=8, pady=(S.SM, 4))

        e = tk.Entry(row, textvariable=var, **WS.ENTRY, width=20)
        e.pack(side="left", fill="x", expand=True, ipady=7, ipadx=6)
        e.bind("<Return>", lambda _: btn_cmd())

        # Placeholder behaviour
        e.insert(0, placeholder)
        e.configure(fg=C.T_MUTED)
        def _fi(_):
            if e.get() == placeholder:
                e.delete(0, "end")
                e.configure(fg=C.T_CREAM)
        def _fo(_):
            if not e.get().strip():
                e.insert(0, placeholder)
                e.configure(fg=C.T_MUTED)
        e.bind("<FocusIn>",  _fi)
        e.bind("<FocusOut>", _fo)

        style = btn_style or WS.BTN_GOLD
        tk.Button(row, text=btn_text, **style,
                  padx=14, pady=7,
                  command=btn_cmd
                  ).pack(side="left", padx=(6, 0))
        return e

    def _make_status(self, parent, var):
        tk.Label(parent, textvariable=var,
                 font=F.MICRO, bg=C.BG1, fg=C.T_GHOST,
                 anchor="w").pack(fill="x", padx=10, pady=(0, 2))


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1: Search by Name
# ══════════════════════════════════════════════════════════════════════════════
class NameTab(BaseTab):
    def _build(self):
        self._make_header("🔍  Search by Name",
                          TAB_ACCENT["name"],
                          "Find any recipe by dish name")

        self._var    = tk.StringVar()
        self._status = tk.StringVar(value="Enter a dish name to search")

        self._make_input(self, self._var, "e.g. chicken tikka, pasta…",
                         "SEARCH", self._search)

        # Quick suggestion chips
        chips_wrap = tk.Frame(self, bg=C.BG1)
        chips_wrap.pack(fill="x", padx=8, pady=(0, 6))
        tk.Label(chips_wrap, text="QUICK:",
                 font=F.LABEL, bg=C.BG1, fg=C.T_GHOST
                 ).pack(side="left", padx=(0, 6))
        for q in Deco.QUICK_SEARCHES:
            HoverButton(chips_wrap, q,
                        command=lambda x=q: self._quick(x),
                        bg=C.BG3, fg=C.T_MUTED,
                        hbg=C.BG4, hfg=C.GOLD,
                        font=F.LABEL, padx=7, pady=3
                        ).pack(side="left", padx=2)

        hdiv(self, C.DIVIDER)
        self._make_status(self, self._status)
        self._lb = self._make_listbox(self)
        self._lb.bind("<<ListboxSelect>>",
                      lambda e: self._on_select(e, self._lb))

    def _search(self):
        q = self._var.get().strip()
        if not q or q.startswith("e.g."):
            return
        self._status.set("Searching…")
        self.detail.show_loading()
        self._lb.delete(0, "end")
        self._thread(lambda: MealAPI.search_name(q),
                     lambda m: self._done(m, q))

    def _quick(self, q):
        self._var.set(q)
        self._search()

    def _done(self, meals, q):
        if not meals:
            self._status.set(f'No results for "{q}" — try a different name')
            self.detail.show_empty(f'No recipes found for "{q}"')
        else:
            self._status.set(f'{len(meals)} result(s) found')
            self._fill_list(self._lb, meals)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2: Search by Ingredient
# ══════════════════════════════════════════════════════════════════════════════
class IngredientTab(BaseTab):
    def _build(self):
        self._make_header("🌿  By Ingredient",
                          TAB_ACCENT["ingredient"],
                          "Discover recipes from what you have")

        self._var    = tk.StringVar()
        self._status = tk.StringVar(value="Pick or type an ingredient")

        self._make_input(self, self._var, "e.g. chicken, pasta, garlic…",
                         "FIND", self._search, WS.BTN_SAGE)

        # Ingredient chip grid
        tk.Label(self, text="  POPULAR",
                 font=F.LABEL, bg=C.BG1, fg=C.T_GHOST,
                 anchor="w", pady=4).pack(fill="x")

        grid_wrap = tk.Frame(self, bg=C.BG1)
        grid_wrap.pack(fill="x", padx=8, pady=(0, 6))

        for i, (emoji, ing) in enumerate(Deco.INGREDIENTS):
            HoverButton(grid_wrap,
                        f"{emoji} {ing}",
                        command=lambda x=ing: self._quick(x),
                        bg=C.BG3, fg=C.T_WARM,
                        hbg=C.SAGE_DEEP, hfg=C.SAGE_LIGHT,
                        font=F.LABEL, padx=8, pady=4
                        ).grid(row=i//3, column=i%3,
                               padx=2, pady=2, sticky="ew")

        for col in range(3):
            grid_wrap.columnconfigure(col, weight=1)

        hdiv(self, C.DIVIDER)
        self._make_status(self, self._status)
        self._lb = self._make_listbox(self)
        self._lb.bind("<<ListboxSelect>>",
                      lambda e: self._on_select(e, self._lb))

    def _search(self):
        ing = self._var.get().strip()
        if not ing or ing.startswith("e.g."):
            return
        self._status.set(f"Finding recipes with {ing}…")
        self.detail.show_loading()
        self._lb.delete(0, "end")
        self._thread(lambda: MealAPI.search_ing(ing),
                     lambda m: self._done(m, ing))

    def _quick(self, ing):
        self._var.set(ing)
        self._search()

    def _done(self, meals, ing):
        if not meals:
            self._status.set(f'Nothing found with "{ing}"')
            self.detail.show_empty(f'No recipes using "{ing}"')
        else:
            self._status.set(f'{len(meals)} recipe(s) with {ing}')
            self._fill_list(self._lb, meals)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3: Browse by Category  (PASTA INCLUDED)
# ══════════════════════════════════════════════════════════════════════════════
class CategoryTab(BaseTab):
    def _build(self):
        self._make_header("📂  By Category",
                          TAB_ACCENT["category"],
                          "Browse all 14 meal categories")

        self._status   = tk.StringVar(value="Select a category")
        self._cat_btns = {}
        self._active   = None

        # Scrollable category grid
        cat_sf = ScrollFrame(self, bg=C.BG1)
        cat_sf.pack(fill="x", padx=6, pady=6)

        grid = tk.Frame(cat_sf.inner, bg=C.BG1)
        grid.pack(fill="x", padx=4)

        for i, (emoji, cat, color) in enumerate(Deco.CATEGORIES):
            btn = HoverButton(
                grid,
                f"{emoji}  {cat}",
                command=lambda c=cat: self._select(c),
                bg=C.BG3, fg=C.T_WARM,
                hbg=C.BG4, hfg=C.T_CREAM,
                abg=C.BG5, afg=C.GOLD,
                font=F.SMALL, padx=10, pady=7,
                anchor="w",
            )
            btn.grid(row=i//2, column=i%2, padx=3, pady=3, sticky="ew")
            self._cat_btns[cat] = btn

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        hdiv(self, C.DIVIDER)
        self._make_status(self, self._status)
        self._lb = self._make_listbox(self)
        self._lb.bind("<<ListboxSelect>>",
                      lambda e: self._on_select(e, self._lb))

    def _select(self, cat):
        if self._active:
            self._cat_btns[self._active].set_active(False)
        self._cat_btns[cat].set_active(True)
        self._active = cat
        self._status.set(f"Loading {cat}…")
        self.detail.show_loading()
        self._lb.delete(0, "end")
        self._thread(lambda: MealAPI.filter_cat(cat),
                     lambda m: self._done(m, cat))

    def _done(self, meals, cat):
        if not meals:
            self._status.set(f"No recipes in {cat}")
            self.detail.show_empty()
        else:
            self._status.set(f'{len(meals)} recipe(s) in {cat}')
            self._fill_list(self._lb, meals)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4: Browse by Area / Cuisine
# ══════════════════════════════════════════════════════════════════════════════
class AreaTab(BaseTab):
    def _build(self):
        self._make_header("🌍  By Cuisine",
                          TAB_ACCENT["area"],
                          "Explore 24 world cuisines")

        self._status    = tk.StringVar(value="Select a world cuisine")
        self._area_btns = {}
        self._active    = None

        area_sf = ScrollFrame(self, bg=C.BG1)
        area_sf.pack(fill="x", padx=6, pady=6)

        grid = tk.Frame(area_sf.inner, bg=C.BG1)
        grid.pack(fill="x", padx=4)

        for i, (flag, area) in enumerate(Deco.AREAS):
            btn = HoverButton(
                grid,
                f"{flag}  {area}",
                command=lambda a=area: self._select(a),
                bg=C.BG3, fg=C.T_WARM,
                hbg=C.VIOLET_D, hfg=C.VIOLET_L,
                abg=C.BG5, afg=C.VIOLET_L,
                font=F.SMALL, padx=10, pady=7,
                anchor="w",
            )
            btn.grid(row=i//2, column=i%2, padx=3, pady=3, sticky="ew")
            self._area_btns[area] = btn

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        hdiv(self, C.DIVIDER)
        self._make_status(self, self._status)
        self._lb = self._make_listbox(self)
        self._lb.bind("<<ListboxSelect>>",
                      lambda e: self._on_select(e, self._lb))

    def _select(self, area):
        if self._active:
            self._area_btns[self._active].set_active(False)
        self._area_btns[area].set_active(True)
        self._active = area
        self._status.set(f"Loading {area} cuisine…")
        self.detail.show_loading()
        self._lb.delete(0, "end")
        self._thread(lambda: MealAPI.filter_area(area),
                     lambda m: self._done(m, area))

    def _done(self, meals, area):
        if not meals:
            self._status.set(f"No recipes for {area}")
            self.detail.show_empty()
        else:
            self._status.set(f'{len(meals)} {area} recipe(s)')
            self._fill_list(self._lb, meals)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5: Random Recipe
# ══════════════════════════════════════════════════════════════════════════════
class RandomTab(BaseTab):
    def _build(self):
        self._make_header("🎲  Random Recipe",
                          TAB_ACCENT["random"],
                          "Discover something unexpected")

        self._history = []

        # Decorative big button
        btn_wrap = tk.Frame(self, bg=C.BG1)
        btn_wrap.pack(fill="x", padx=16, pady=16)

        tk.Button(btn_wrap,
                  text="✦  Surprise Me!  ✦",
                  font=(F.SERIF, 14, "bold"),
                  bg=C.GOLD_DEEP, fg=C.GOLD_LIGHT,
                  activebackground=C.GOLD,
                  activeforeground=C.BLACK,
                  relief="flat", cursor="hand2",
                  pady=18,
                  command=self._fetch
                  ).pack(fill="x")

        tk.Label(btn_wrap,
                 text="Click to discover a random recipe from any cuisine",
                 font=F.MICRO, bg=C.BG1, fg=C.T_GHOST,
                 pady=6).pack()

        # History section
        hdiv(self, C.DIVIDER)
        tk.Label(self, text="  ◦  RECENTLY DISCOVERED",
                 font=F.LABEL, bg=C.BG1, fg=C.T_GHOST,
                 anchor="w", pady=5).pack(fill="x")
        hdiv(self, C.DIVIDER)

        self._lb = self._make_listbox(self)
        self._lb.bind("<<ListboxSelect>>",
                      lambda e: self._on_select(e, self._lb))

    def _fetch(self):
        self.detail.show_loading()
        def fetch():
            return MealAPI.random()
        def done(meal):
            if not meal:
                self.detail.show_empty("Could not fetch a random recipe.")
                return
            self._cache[meal["idMeal"]] = meal
            self._history.insert(0, meal)
            # Keep only last 20
            self._history[:] = self._history[:20]
            self._meals = self._history
            self._lb.delete(0, "end")
            for m in self._history:
                self._lb.insert("end", f"   {m['strMeal']}")
            self.detail.render(meal)
        self._thread(fetch, done)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class RecipeVault(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("The Recipe Vault")
        self.geometry("1300x820")
        self.minsize(1000, 660)
        self.configure(bg=C.BG0)
        self._build()

    def _build(self):
        # ── Top chrome bar ───────────────────────────────────────────────────
        chrome = tk.Frame(self, bg=C.BG0, height=40)
        chrome.pack(fill="x")
        chrome.pack_propagate(False)

        # Left: app name
        tk.Label(chrome,
                 text="  🍽  THE RECIPE VAULT",
                 font=(F.SERIF, 12, "bold"),
                 bg=C.BG0, fg=C.GOLD,
                 padx=4).pack(side="left", pady=6)

        # Right: subtitle
        tk.Label(chrome,
                 text="Powered by TheMealDB  ",
                 font=F.MICRO,
                 bg=C.BG0, fg=C.T_GHOST
                 ).pack(side="right", pady=6)

        # Gold bottom border
        tk.Frame(self, bg=C.GOLD_DIM, height=1).pack(fill="x")

        # ── Layout: sidebar | search panel | detail ──────────────────────────
        body = tk.Frame(self, bg=C.BG0)
        body.pack(fill="both", expand=True)

        # Sidebar
        self._sidebar = SideBar(body, self._switch)
        self._sidebar.pack(side="left", fill="y")

        vdiv(body, C.DIVIDER)

        # Middle search/browse panel
        self._panel = tk.Frame(body, bg=C.BG1, width=370)
        self._panel.pack(side="left", fill="y")
        self._panel.pack_propagate(False)

        vdiv(body, C.DIVIDER)

        # Detail panel
        self._detail = DetailPanel(body)
        self._detail.pack(side="left", fill="both", expand=True)

        # Create all tab panels
        self._tabs = {
            "name":       NameTab(self._panel, self._detail),
            "ingredient": IngredientTab(self._panel, self._detail),
            "category":   CategoryTab(self._panel, self._detail),
            "area":       AreaTab(self._panel, self._detail),
            "random":     RandomTab(self._panel, self._detail),
        }

        # Show default tab
        self._sidebar.activate("name")

    def _switch(self, key):
        for tab in self._tabs.values():
            tab.pack_forget()
        self._tabs[key].pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = RecipeVault()
    app.mainloop()