"""
theme.py ── Visual Design System · The Recipe Vault
════════════════════════════════════════════════════
Aesthetic: Midnight Spice Market
Deep obsidian backgrounds, saffron gold, rose copper,
ivory cream text. Inspired by candlelit kitchens
and old-world spice bazaars.
"""


# ══════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════════════════
class C:
    # Backgrounds (darkest → lightest)
    BG0        = "#09080a"
    BG1        = "#110f14"
    BG2        = "#1a1720"
    BG3        = "#221e2c"
    BG4        = "#2c2838"
    BG5        = "#363245"

    # Saffron Gold (primary)
    GOLD       = "#f0c060"
    GOLD_LIGHT = "#ffd98a"
    GOLD_DEEP  = "#9a7030"
    GOLD_DIM   = "#5a4020"

    # Rose Copper (warm cta)
    ROSE       = "#e07060"
    ROSE_LIGHT = "#f09080"
    ROSE_DEEP  = "#8a3828"

    # Sage (ingredient / nature)
    SAGE       = "#80b878"
    SAGE_LIGHT = "#a0d898"
    SAGE_DEEP  = "#3c5c38"

    # Violet (area/cuisine)
    VIOLET     = "#9880c8"
    VIOLET_L   = "#c0b0e8"
    VIOLET_D   = "#483860"

    # Text
    T_CREAM    = "#f8f0e0"
    T_WARM     = "#d0c4a8"
    T_MUTED    = "#807888"
    T_GHOST    = "#3c3448"

    # Borders
    B_HARD     = "#38304a"
    B_SOFT     = "#201c2c"
    B_GOLD     = "#604820"

    # Misc
    WHITE      = "#ffffff"
    BLACK      = "#000000"
    DIVIDER    = "#2a2438"


# ══════════════════════════════════════════════════════════
#  TYPOGRAPHY
# ══════════════════════════════════════════════════════════
class F:
    SERIF  = "Palatino Linotype"
    MONO   = "Consolas"

    S_HERO  = 24
    S_TITLE = 17
    S_HEAD  = 13
    S_BODY  = 10
    S_SMALL = 9
    S_MICRO = 8
    S_NANO  = 7

    HERO    = (SERIF, S_HERO,  "bold")
    TITLE   = (SERIF, S_TITLE, "bold")
    HEADING = (SERIF, S_HEAD,  "bold")
    SUBHEAD = (SERIF, S_HEAD,  "normal")
    CARD    = (SERIF, 11,      "bold")
    BODY    = (MONO,  S_BODY,  "normal")
    BODY_B  = (MONO,  S_BODY,  "bold")
    SMALL   = (MONO,  S_SMALL, "normal")
    SMALL_B = (MONO,  S_SMALL, "bold")
    MICRO   = (MONO,  S_MICRO, "normal")
    MICRO_B = (MONO,  S_MICRO, "bold")
    LABEL   = (MONO,  S_NANO,  "bold")


# ══════════════════════════════════════════════════════════
#  SPACING
# ══════════════════════════════════════════════════════════
class S:
    XS  = 4
    SM  = 8
    MD  = 14
    LG  = 20
    XL  = 30


# ══════════════════════════════════════════════════════════
#  WIDGET STYLES
# ══════════════════════════════════════════════════════════
class WS:
    FRAME      = dict(bg=C.BG1)
    FRAME_CARD = dict(bg=C.BG3, highlightthickness=1,
                      highlightbackground=C.B_HARD)
    CANVAS     = dict(bg=C.BG1, highlightthickness=0, bd=0)

    LISTBOX    = dict(
        bg=C.BG2, fg=C.T_WARM,
        selectbackground=C.BG5, selectforeground=C.GOLD,
        activestyle="none", relief="flat", bd=0,
        highlightthickness=0, font=F.SMALL,
    )

    SCROLLBAR  = dict(
        bg=C.BG3, troughcolor=C.BG0,
        relief="flat", bd=0, width=4,
        activebackground=C.GOLD_DIM,
    )

    ENTRY      = dict(
        bg=C.BG3, fg=C.T_CREAM,
        insertbackground=C.GOLD,
        relief="flat", bd=0,
        highlightthickness=2,
        highlightbackground=C.B_HARD,
        highlightcolor=C.GOLD,
        font=F.BODY,
    )

    BTN_GOLD   = dict(
        bg=C.GOLD_DEEP, fg=C.T_CREAM,
        activebackground=C.GOLD,
        activeforeground=C.BLACK,
        relief="flat", bd=0, cursor="hand2",
        font=F.SMALL_B,
    )

    BTN_ROSE   = dict(
        bg=C.ROSE_DEEP, fg=C.WHITE,
        activebackground=C.ROSE,
        activeforeground=C.WHITE,
        relief="flat", bd=0, cursor="hand2",
        font=F.SMALL_B,
    )

    BTN_GHOST  = dict(
        bg=C.BG3, fg=C.T_MUTED,
        activebackground=C.BG4,
        activeforeground=C.T_WARM,
        relief="flat", bd=0, cursor="hand2",
        font=F.SMALL,
        highlightthickness=1,
        highlightbackground=C.B_HARD,
        highlightcolor=C.GOLD_DEEP,
    )

    BTN_SAGE   = dict(
        bg=C.SAGE_DEEP, fg=C.WHITE,
        activebackground=C.SAGE,
        activeforeground=C.BLACK,
        relief="flat", bd=0, cursor="hand2",
        font=F.SMALL_B,
    )

    BTN_VIOLET = dict(
        bg=C.VIOLET_D, fg=C.WHITE,
        activebackground=C.VIOLET,
        activeforeground=C.BLACK,
        relief="flat", bd=0, cursor="hand2",
        font=F.SMALL_B,
    )


# ══════════════════════════════════════════════════════════
#  TAB STYLES
# ══════════════════════════════════════════════════════════
class TS:
    ACTIVE = dict(
        bg=C.BG5, fg=C.GOLD,
        font=F.MICRO_B, relief="flat", bd=0,
        cursor="hand2", padx=16, pady=11, anchor="w",
    )
    INACTIVE = dict(
        bg=C.BG2, fg=C.T_MUTED,
        font=F.MICRO, relief="flat", bd=0,
        cursor="hand2", padx=16, pady=11, anchor="w",
        activebackground=C.BG3,
        activeforeground=C.T_WARM,
    )


# ══════════════════════════════════════════════════════════
#  ACCENT COLOUR PER TAB
# ══════════════════════════════════════════════════════════
TAB_ACCENT = {
    "name":       C.GOLD,
    "ingredient": C.SAGE,
    "category":   C.ROSE,
    "area":       C.VIOLET,
    "random":     C.GOLD_LIGHT,
}


# ══════════════════════════════════════════════════════════
#  CONTENT DATA
# ══════════════════════════════════════════════════════════
class Deco:

    # All MealDB categories — PASTA ADDED ✅
    CATEGORIES = [
        ("🥩", "Beef",          C.ROSE),
        ("🍳", "Breakfast",     C.GOLD),
        ("🍗", "Chicken",       C.GOLD_DEEP),
        ("🍰", "Dessert",       C.ROSE_LIGHT),
        ("🐐", "Goat",          C.SAGE),
        ("🐑", "Lamb",          C.SAGE_DEEP),
        ("🍔", "Miscellaneous", C.T_MUTED),
        ("🍝", "Pasta",         C.ROSE),       # ← PASTA ✅
        ("🥓", "Pork",          C.ROSE_DEEP),
        ("🐟", "Seafood",       C.VIOLET),
        ("🥬", "Side",          C.SAGE),
        ("🥗", "Starter",       C.GOLD),
        ("🌿", "Vegan",         C.SAGE_LIGHT),
        ("🥦", "Vegetarian",    C.SAGE),
    ]

    AREAS = [
        ("🇺🇸", "American"),    ("🇬🇧", "British"),
        ("🇨🇦", "Canadian"),    ("🇨🇳", "Chinese"),
        ("🇫🇷", "French"),      ("🇬🇷", "Greek"),
        ("🇮🇳", "Indian"),      ("🇮🇪", "Irish"),
        ("🇮🇹", "Italian"),     ("🇯🇵", "Japanese"),
        ("🇲🇾", "Malaysian"),   ("🇲🇽", "Mexican"),
        ("🇲🇦", "Moroccan"),    ("🇳🇱", "Dutch"),
        ("🇵🇭", "Filipino"),    ("🇵🇱", "Polish"),
        ("🇵🇹", "Portuguese"),  ("🇷🇺", "Russian"),
        ("🇪🇸", "Spanish"),     ("🇹🇭", "Thai"),
        ("🇹🇳", "Tunisian"),    ("🇹🇷", "Turkish"),
        ("🇻🇳", "Vietnamese"),  ("🌍", "Unknown"),
    ]

    INGREDIENTS = [
        ("🍗", "Chicken"),    ("🥩", "Beef"),       ("🐟", "Salmon"),
        ("🍝", "Pasta"),      ("🍚", "Rice"),        ("🍅", "Tomato"),
        ("🧄", "Garlic"),     ("🧅", "Onion"),       ("🍋", "Lemon"),
        ("🧈", "Butter"),     ("🥚", "Eggs"),        ("🧀", "Cheese"),
        ("🍄", "Mushrooms"),  ("🥬", "Spinach"),     ("🥔", "Potato"),
        ("🌶️",  "Chilli"),    ("🫒", "Olive Oil"),   ("🧂", "Salt"),
    ]

    QUICK_SEARCHES = [
        "Chicken Tikka Masala", "Spaghetti Bolognese", "Fish Tacos",
        "Beef Curry", "Beef Burger", "Tomato Soup", "Pad Thai",
    ]