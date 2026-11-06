"""Render the screenshots/ part of this set: python render_screens.py OUTDIR [CHROME]

60 app-like screens (chat, settings, inbox, table, terminal, dialog, dashboard, form, code, notification) from text
written for this set, in light and dark themes, at 13-18 px, in sans, serif and monospace fonts. The ground truth is
the browser's own innerText of what it rendered, so it matches the pixels. CC0. random.Random(0) picks everything."""
import os, random, sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1]) / "screenshots"
R = random.Random(0)

NAMES = ["Maya Okafor", "Luis Ferreira", "Ana Kovač", "Tom Becker", "Priya Raman", "Jonas Lind", "Sara Haddad",
         "Ken Ito", "Elena Rossi", "Omar Said", "Nina Petrova", "Ben Carter"]
SUBJECTS = ["Invoice 2041 is overdue", "Your order has shipped", "Meeting moved to Thursday 10:30",
            "Password changed successfully", "Quarterly report draft v3", "Welcome to the beta",
            "Reminder: dentist appointment", "Build failed on main", "Your refund of $18.40 was approved",
            "New sign-in from Firefox on Windows", "Flight LH 1412 boarding at gate B22", "Lunch on Friday?"]
CHAT = ["are we still on for tomorrow?", "yes, 7pm at the usual place", "can you send me the slides",
        "sent! check your inbox", "the train is 15 minutes late", "no worries, I'll grab a table",
        "did the deploy go through?", "rolled back, the migration timed out", "ok let's try again after lunch",
        "happy birthday!!", "thanks, see you at 8", "I left the keys under the blue pot"]
SETTINGS = [("Dark mode", "On"), ("Notifications", "Mentions only"), ("Language", "English (UK)"),
            ("Auto-update", "Off"), ("Storage used", "41.7 GB of 64 GB"), ("Backup", "Daily at 02:00"),
            ("Two-factor authentication", "Enabled"), ("Time zone", "Europe/Zagreb"), ("Font size", "Medium"),
            ("Battery saver", "When below 20%")]
TERM = ["$ git status", "On branch main", "Your branch is ahead of 'origin/main' by 2 commits.",
        "$ python -m pytest -q", "48 passed, 2 skipped in 3.91s", "$ docker ps",
        "CONTAINER ID   IMAGE          STATUS", "3f2a9c1d8e7b   nginx:1.27     Up 4 hours",
        "$ df -h /", "/dev/sda1  234G  151G   72G  68% /", "$ curl -I https://example.org", "HTTP/2 200"]
CODE = ["def total(items):", "    return sum(i.price * i.qty for i in items)", "", "for user in users:",
        "    if user.active and not user.banned:", "        send_welcome(user.email)", "",
        "const limit = 25;", "fetch(`/api/orders?page=${page}`)", "  .then(r => r.json())"]
ERRORS = ["The file could not be saved because the disk is full.", "Connection lost. Retrying in 10 seconds.",
          "You have unsaved changes. Close anyway?", "This link has expired. Request a new one."]
FONTS = ["DejaVu Sans", "DejaVu Serif", "Lato", "DejaVu Sans Mono"]


def money():
    return f"{R.choice(['$', '€', '£'])}{R.randint(1, 9999):,}.{R.randint(0, 99):02d}"


def screen(kind):
    if kind == "chat":
        msgs = R.sample(CHAT, 6)
        return "<h2>" + R.choice(NAMES) + "</h2>" + "".join(
            f'<p class="b {"me" if i % 2 else ""}">{m}<small>{R.randint(8, 22):02d}:{R.randint(0, 59):02d}</small></p>'
            for i, m in enumerate(msgs))
    if kind == "settings":
        return "<h2>Settings</h2>" + "".join(f"<div class=row><span>{k}</span><b>{v}</b></div>" for k, v in R.sample(SETTINGS, 6))
    if kind == "inbox":
        return "<h2>Inbox (" + str(R.randint(3, 99)) + ")</h2>" + "".join(
            f"<div class=row><span><b>{n}</b><br>{s}</span><small>{R.choice(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])}</small></div>"
            for n, s in zip(R.sample(NAMES, 5), R.sample(SUBJECTS, 5)))
    if kind == "table":
        rows = "".join(f"<tr><td>{R.randint(1000, 9999)}</td><td>{n}</td><td>{R.choice(['Paid', 'Pending', 'Refunded'])}</td><td>{money()}</td></tr>"
                       for n in R.sample(NAMES, 6))
        return f"<h2>Orders</h2><table><tr><th>ID</th><th>Customer</th><th>Status</th><th>Amount</th></tr>{rows}</table>"
    if kind == "terminal":
        i = R.randrange(0, len(TERM) - 6)
        return '<pre class=term>' + "\n".join(TERM[i:i + 7]) + "</pre>"
    if kind == "dialog":
        return f'<div class=dlg><h2>{R.choice(["Error", "Warning", "Heads up"])}</h2><p>{R.choice(ERRORS)}</p><button>Cancel</button> <button>OK</button></div>'
    if kind == "dashboard":
        return "<h2>This week</h2>" + "".join(
            f"<div class=tile><small>{k}</small><b>{v}</b></div>"
            for k, v in [("Revenue", money()), ("Orders", f"{R.randint(10, 999):,}"), ("Refund rate", f"{R.uniform(0, 9):.1f}%"),
                         ("Visitors", f"{R.randint(100, 99999):,}")])
    if kind == "form":
        return "<h2>Create account</h2>" + "".join(f"<label>{l}<input value='{v}'></label>" for l, v in
                                                     [("Full name", R.choice(NAMES)), ("Email", "someone@example.com"),
                                                      ("Phone", f"+1 555 {R.randint(100, 999)} {R.randint(1000, 9999)}")]) + "<button>Sign up</button>"
    if kind == "code":
        i = R.randrange(0, 4)
        return "<pre class=code>" + "\n".join(f"{n + 1:>3}  {l}" for n, l in enumerate(CODE[i:i + 7])) + "</pre>"
    return (f"<div class=note><b>{R.choice(['Calendar', 'Bank', 'Messages', 'Delivery'])}</b><p>{R.choice(SUBJECTS)}</p>"
            f"<small>{R.randint(1, 59)} min ago</small></div>")


def page(body, dark, font, px, width):
    bg, fg, card = ("#16181d", "#e6e6e6", "#23262d") if dark else ("#ffffff", "#1d1d1f", "#f2f3f5")
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
body{{margin:0;padding:22px;background:{bg};color:{fg};font:{px}px/1.45 '{font}';width:{width}px}}
h2{{font-size:1.3em;margin:0 0 12px}}.row{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #8884}}
.b{{background:{card};border-radius:14px;padding:8px 12px;margin:6px 0;max-width:70%}}.b.me{{margin-left:auto;background:#2f6fde;color:#fff}}
small{{opacity:.7;margin-left:10px;font-size:.8em}}table{{border-collapse:collapse;width:100%}}td,th{{padding:7px;border-bottom:1px solid #8884;text-align:left}}
pre{{font:{px}px/1.5 'DejaVu Sans Mono';background:{card};padding:12px;border-radius:8px;margin:0}}.term{{background:#0c0c0c;color:#d7f7d7}}
.dlg{{background:{card};padding:18px;border-radius:12px}}button{{font:inherit;padding:6px 14px;margin-top:8px}}
.tile{{display:inline-block;background:{card};border-radius:10px;padding:10px 14px;margin:5px;min-width:120px}}.tile b{{display:block;font-size:1.4em}}
label{{display:block;margin:8px 0}}input{{display:block;font:inherit;padding:5px;width:90%;margin-top:3px}}.note{{background:{card};padding:12px;border-radius:12px}}
</style></head><body>{body}</body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    kinds = ["chat", "settings", "inbox", "table", "terminal", "dialog", "dashboard", "form", "code", "notification"]
    chrome = sys.argv[2] if len(sys.argv) > 2 else None
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": chrome} if chrome else {}))
        pg = b.new_page(device_scale_factor=1)
        for n in range(60):
            kind = kinds[n % len(kinds)]
            dark, font, px = R.random() < 0.4, R.choice(FONTS), R.choice([13, 14, 15, 16, 18])
            width = R.choice([360, 480, 640, 800])
            pg.set_content(page(screen(kind), dark, font, px, width))
            pg.wait_for_timeout(50)
            name = f"{n:02d}-{kind}-{'dark' if dark else 'light'}"
            pg.screenshot(path=str(OUT / f"{name}.png"), clip={"x": 0, "y": 0, "width": width + 44,
                                                              "height": pg.evaluate("document.body.scrollHeight")})
            # inputs: innerText skips their values, but they are on screen
            text = pg.evaluate("""() => { const vals = [...document.querySelectorAll('input')].map(i => i.value);
                return document.body.innerText + (vals.length ? '\\n' + vals.join('\\n') : ''); }""")
            (OUT / f"{name}.gt.txt").write_text(text.strip() + "\n", encoding="utf-8")
        b.close()


if __name__ == "__main__":
    main()
