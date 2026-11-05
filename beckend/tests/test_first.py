from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

FAKE_ITEMS = [
    {"market_hash_name": "AK-47 | Redline (Field-Tested)", "min_price": 50.0},
    {"market_hash_name": "AWP | Asiimov (Field-Tested)", "min_price": 120.0},
    {"market_hash_name": "Glock-18 | Fade (Factory New)", "min_price": 900.0},
]

# def test_skins_returns_200():
#     response = client.get("/skins")
#     assert response.status_code == 200

def test_skins_returns_fake_data(monkeypatch, tmp_path):
    # 1. cache wskazuje na plik, który jeszcze nie istnieje (tmp_path to
    #    tymczasowy folder, sprzątany po teście), więc kod pójdzie do "else"
    monkeypatch.setattr(main, "CACHE_FILE", tmp_path / "items.json")

    # 2. zamiast prawdziwego Skinporta zwracamy sztuczne dane
    monkeypatch.setattr(main, "fetch_items", lambda: FAKE_ITEMS)

    response = client.get("/skins")

    assert response.status_code == 200
    assert response.json() == FAKE_ITEMS