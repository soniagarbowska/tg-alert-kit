"""Render karty alertu jako obraz PNG (HTML/CSS -> headless Chrome).

To jest droga do PRAWDZIWIE ladnych komunikatow w Telegramie: Telegram nie
renderuje HTML/CSS w tekscie, ale renderuje OBRAZ. Wiec robimy piekna karte
w HTML/CSS i zrzucamy ja Chromem do PNG, potem wysylamy jako zdjecie.

Atomowe i powtarzalne: dane -> card_png(...) -> sciezka do PNG.

Wymaga: google-chrome (lub chromium) w PATH.
"""
from __future__ import annotations
import os, html, shutil, subprocess, tempfile, time, hashlib

_DIR = os.path.dirname(os.path.abspath(__file__))
_TPL = os.path.join(os.path.dirname(_DIR), "cards", "card_template.html")
# Katalog dozwolony do wysylki media przez OCPlatform = workspace agenta.
# (Zweryfikowane 2026-06-08: ~/.ocplatform/media/* ODRZUcane, ~/hugo-works OK.)
_OUTDIR = os.environ.get("TG_ALERT_CARD_DIR",
                         os.path.expanduser("~/hugo-works/alert-cards"))

# Paleta wg wagi: (gradient paska, kolor akcentu, tlo notki, ikona, slowo)
_THEME = {
    "critical": ("linear-gradient(135deg,#e0344b,#a3142b)", "#e0344b", "rgba(224,52,75,.12)", "\U0001f6e1\uFE0F", "Krytyczne"),
    "firing":   ("linear-gradient(135deg,#e0344b,#a3142b)", "#e0344b", "rgba(224,52,75,.12)", "\U0001f6e1\uFE0F", "Krytyczne"),
    "warn":     ("linear-gradient(135deg,#f0991e,#c2710a)", "#f0991e", "rgba(240,153,30,.12)", "\u26A0\uFE0F", "Uwaga"),
    "warning":  ("linear-gradient(135deg,#f0991e,#c2710a)", "#f0991e", "rgba(240,153,30,.12)", "\u26A0\uFE0F", "Uwaga"),
    "info":     ("linear-gradient(135deg,#2f7ef0,#1857c2)", "#2f7ef0", "rgba(47,126,240,.12)", "\u2139\uFE0F", "Informacja"),
    "ok":       ("linear-gradient(135deg,#1fae66,#0e8a4c)", "#1fae66", "rgba(31,174,102,.12)", "\u2705", "OK"),
    "resolved": ("linear-gradient(135deg,#1fae66,#0e8a4c)", "#1fae66", "rgba(31,174,102,.12)", "\u2705", "Rozwiazane"),
}

# Pola pokazywane monospace (dane techniczne)
_MONO_KEYS = ("ip", "adres", "host", "port", "login", "uzytkownik", "user",
              "plik", "sciezka", "path", "url", "domena", "hash", "id", "kwota", "cena")


def _is_mono(key: str) -> bool:
    k = (key or "").lower()
    return any(tok in k for tok in _MONO_KEYS)


def _chrome() -> str | None:
    for b in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        p = shutil.which(b)
        if p:
            return p
    return None


def card_html(
    title: str,
    fields: list[tuple[str, str]],
    severity: str = "warn",
    note: str | None = None,
    badge: str | None = None,
    foot_left: str | None = None,
    alert_id: str = "",
) -> str:
    sev = (severity or "warn").lower()
    grad, accent, note_bg, icon, sev_label = _THEME.get(sev, _THEME["warn"])

    rows = []
    for k, v in (fields or []):
        cls = "v mono" if _is_mono(k) else "v"
        rows.append(
            f'<div class="row"><div class="k">{html.escape(str(k))}</div>'
            f'<div class="{cls}">{html.escape(str(v))}</div></div>'
        )
    rows_html = "\n".join(rows)

    note_html = ""
    if note:
        note_html = f'<div class="note">{html.escape(note)}</div>'

    badge = badge or sev_label
    foot_left = foot_left or time.strftime("%Y-%m-%d %H:%M")

    tpl = open(_TPL, encoding="utf-8").read()
    out = (tpl
        .replace("__ICON__", icon)
        .replace("__TITLE__", html.escape(title))
        .replace("__SEVLABEL__", html.escape(sev_label))
        .replace("__BADGE__", html.escape(badge))
        .replace("__ROWS__", rows_html)
        .replace("__NOTE__", note_html)
        .replace("__FOOTLEFT__", html.escape(foot_left))
        .replace("__ID__", html.escape(alert_id or "")))
    # wstrzyknij zmienne CSS (kolory wg wagi)
    out = out.replace("<div class=\"card\">",
        f'<div class="card" style="--accent-grad:{grad};--accent:{accent};--note-bg:{note_bg};">')
    return out


def card_png(
    title: str,
    fields: list[tuple[str, str]],
    severity: str = "warn",
    note: str | None = None,
    badge: str | None = None,
    foot_left: str | None = None,
    alert_id: str = "",
    out_path: str | None = None,
) -> str:
    """Renderuje karte do PNG (przezroczyste tlo). Zwraca sciezke do pliku."""
    chrome = _chrome()
    if not chrome:
        raise RuntimeError("brak google-chrome/chromium w PATH")

    os.makedirs(_OUTDIR, exist_ok=True)
    htmltext = card_html(title, fields, severity, note, badge, foot_left, alert_id)

    tag = alert_id or hashlib.md5(title.encode()).hexdigest()[:8]
    if not out_path:
        out_path = os.path.join(_OUTDIR, f"card-{tag}-{int(time.time())}.png")

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(htmltext)
        html_path = f.name

    try:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--force-device-scale-factor=2",           # 2x = ostro (retina)
            "--default-background-color=00000000",      # przezroczyste tlo
            "--hide-scrollbars",
            "--window-size=1000,1600",   # duzo wysokosci, przytniemy potem
            f"--screenshot={out_path}",
            f"file://{html_path}",
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
    finally:
        try: os.unlink(html_path)
        except OSError: pass

    if not os.path.exists(out_path):
        raise RuntimeError("Chrome nie wygenerowal PNG")

    # Przytnij przezroczyste marginesy (karta ma realna wysokosc < 1600)
    try:
        from PIL import Image
        im = Image.open(out_path).convert("RGBA")
        bbox = im.getbbox()           # ramka niepustych (nieprzezroczystych) pikseli
        if bbox:
            pad = 24
            l, t, r, b = bbox
            l = max(0, l - pad); t = max(0, t - pad)
            r = min(im.width, r + pad); b = min(im.height, b + pad)
            im.crop((l, t, r, b)).save(out_path)
    except Exception:
        pass
    return out_path
