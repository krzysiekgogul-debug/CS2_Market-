import json
import urllib.parse
import httpx

STEAM_ACTIONS_URL = "https://steamcommunity.com/market/actions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-valve-request-type": "queryAction",
}


CURRENCY_MAP = {
    "$": "USD",
    "€": "EUR",
    "zł": "PLN",
    "£": "GBP",
}


def parse_price(price_str: str | None) -> tuple[float | None, str | None]:
    if not price_str:
        return None, None

    # 1. Szukamy symbolu waluty w tekście
    currency = "UNKNOWN"
    for symbol, code in CURRENCY_MAP.items():
        if symbol in price_str:
            currency = code
            break

    # 2. Wyciągamy samą liczbę (cyfry oraz kropkę/przecinek)
    cleaned = "".join(char for char in price_str if char.isdigit() or char in ".,")
    cleaned = cleaned.replace(",", ".")

    try:
        amount = float(cleaned)
    except ValueError:
        amount = None

    return amount, currency


def fetch_steam_listings(group_id: str, start: int = 0) -> list[dict]:
    params = {
        "q": "QueryListingsForItem",
        "qp": json.dumps([{
            "appid": 730,
            "strItemName": group_id,
            "start": start,
            "filters": {},
            "accessoryFilters": {},
            "propertyFilters": {},
        }]),
    }

    with httpx.Client(headers=HEADERS, follow_redirects=False) as client:
        response = client.get(STEAM_ACTIONS_URL, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch data. HTTP status code: {response.status_code}")
        return []

    raw_listings = response.json().get("data", {}).get("listings") or []
    clean_listings = []

    for item in raw_listings:
        asset = item.get("asset") or {}
        desc = asset.get("description") or {}

        float_val = None
        paint_seed = None
        for prop in asset.get("asset_properties") or []:
            if prop.get("propertyid") == 2:
                float_val = prop.get("value")
            elif prop.get("propertyid") == 1:
                paint_seed = prop.get("value")

        icon_hash = desc.get("icon_url")
        image_url = (
            f"https://community.fastly.steamstatic.com/economy/image/{icon_hash}"
            if icon_hash else None
        )

        hash_name = desc.get("market_hash_name", "")
        steam_market_url = (
            f"https://steamcommunity.com/market/listings/730/{urllib.parse.quote(hash_name)}"
            if hash_name else None
        )

        actions = desc.get("market_actions") or desc.get("actions") or []
        inspect_link = actions[0].get("link") if actions else None

        raw_price = item.get("strSubtotal")
        price_value, currency_code = parse_price(raw_price)

        listing_data = {
            "listing_id": item.get("listingid"),
            "full_name": hash_name,
            "name_in_group": desc.get("market_name_inside_group"),
            "type": desc.get("type"),
            "price_float": price_value,
            "currency": currency_code,
            "float_value": float_val,
            "paint_seed": paint_seed,
            "image_url": image_url,
            "steam_market_url": steam_market_url,
            "inspect_link": inspect_link,
            "bucket_group_id": desc.get("market_bucket_group_id"),
            "bucket_id": desc.get("market_bucket_id"),
            "enhanced_appearances": asset.get("enhanced_appearances"),
        }
        clean_listings.append(listing_data)

    return clean_listings


def save_listings_to_json(listings: list[dict], filename: str = "clean_listings.json") -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(listings, file, indent=4, ensure_ascii=False)
    print(f"Saved {len(listings)} listings to {filename}.")

def main():
    fetched_listings = fetch_steam_listings(group_id="G1807209A023004", start=0)
    if fetched_listings:
        save_listings_to_json(fetched_listings)


if __name__ == "__main__":
     main()