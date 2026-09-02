import json
import os
import time
from pathlib import Path

import requests

ML_SEARCH = "https://api.mercadolibre.com/sites/MLB/search"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

DATA_DIR = Path("data")
SENT_FILE = DATA_DIR / "sent.json"
AFFILIATE_FILE = DATA_DIR / "affiliate_links.json"

MIN_DISCOUNT = float(os.getenv("MIN_DISCOUNT", "20"))
MAX_PRICE = float(os.getenv("MAX_PRICE", "1000"))
MAX_POSTS = int(os.getenv("MAX_POSTS", "5"))

SEARCH_TERMS = [
    x.strip()
    for x in os.getenv(
        "SEARCH_TERMS",
        "fone bluetooth,smartwatch,air fryer,creatina,furadeira,organizador de cozinha"
    ).split(",")
    if x.strip()
]

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {"User-Agent": "AchadinhosDoVo/1.0"}


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def money(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def discount_percent(item):
    price = item.get("price")
    original = item.get("original_price")

    if not price or not original or original <= price:
        return 0.0

    return round((1 - price / original) * 100, 1)


def search_products(term):
    response = requests.get(
        ML_SEARCH,
        params={"q": term, "limit": 50, "sort": "relevance"},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("results", [])


def collect_candidates():
    all_items = {}

    for term in SEARCH_TERMS:
        print(f"Buscando: {term}")

        try:
            items = search_products(term)
        except Exception as exc:
            print(f"Erro em '{term}': {exc}")
            continue

        for item in items:
            item_id = item.get("id")
            price = item.get("price")

            if not item_id or not price:
                continue

            if price > MAX_PRICE:
                continue

            if discount_percent(item) < MIN_DISCOUNT:
                continue

            all_items[item_id] = item

    return sorted(
        all_items.values(),
        key=lambda x: discount_percent(x),
        reverse=True,
    )


def get_affiliate_link(item_id, affiliate_links):
    link = str(affiliate_links.get(item_id, "")).strip()

    if not link:
        return None

    if "COLE_AQUI" in link.upper() or "SEU-LINK" in link.upper():
        return None

    return link


def build_message(item, link):
    title = item.get("title", "Oferta")
    price = item.get("price")
    original = item.get("original_price")
    discount = discount_percent(item)

    lines = [
        "🔥 ACHADINHO DO VÔ",
        "",
        f"🛍️ {title}",
        "",
    ]

    if original and discount:
        lines.extend([
            f"❌ De: {money(original)}",
            f"🔥 Por: {money(price)}",
            f"💥 {discount:.0f}% OFF",
        ])
    else:
        lines.append(f"💰 {money(price)}")

    lines.extend([
        "",
        "👉 Conferir oferta:",
        link,
        "",
        "⚠️ Preço e estoque podem mudar sem aviso.",
        "📦 Achadinhos do Vô",
    ])

    return "\n".join(lines)


def send_telegram(text):
    response = requests.post(
        TELEGRAM_API.format(token=BOT_TOKEN),
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"Telegram HTTP {response.status_code}: {response.text}"
        )


def main():
    DATA_DIR.mkdir(exist_ok=True)

    sent = load_json(SENT_FILE, {})
    affiliate_links = load_json(AFFILIATE_FILE, {})

    candidates = collect_candidates()

    print(f"Produtos candidatos: {len(candidates)}")
    print(f"Links de afiliado cadastrados: {len(affiliate_links)}")

    posted = 0

    for item in candidates:
        if posted >= MAX_POSTS:
            break

        item_id = item["id"]

        if item_id in sent:
            continue

        link = get_affiliate_link(item_id, affiliate_links)

        if not link:
            print(f"Sem link de afiliado cadastrado: {item_id}")
            continue

        try:
            send_telegram(build_message(item, link))

            sent[item_id] = {
                "posted_at": int(time.time()),
                "title": item.get("title"),
                "price": item.get("price"),
            }
            save_json(SENT_FILE, sent)

            posted += 1
            print(f"Publicado: {item_id}")
            time.sleep(2)

        except Exception as exc:
            print(f"Erro publicando {item_id}: {exc}")

    print(f"Total publicado nesta execução: {posted}")


if __name__ == "__main__":
    main()
