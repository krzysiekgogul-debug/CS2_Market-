import httpx
import pytest
import respx

from search_skins import URL, fetch_items


# TEST 1: Sprawdzamy, czy przy poprawnym JSON-ie funkcja zwraca listę słowników
@pytest.mark.asyncio
@respx.mock
async def test_fetch_items_success():
    # 1. ARRANGE (Przygotuj udawaną odpowiedź ze Skinportu)
    fake_api_response = [
        {"market_hash_name": "AK-47 | Redline (Field-Tested)", "min_price": 50.0},
        {"market_hash_name": "AWP | Asiimov (Field-Tested)", "min_price": 350.0},
    ]
    # Przechwytujemy każde zapytanie GET na adres URL ze Skinportu i zwracamy nasz fake JSON
    respx.get(URL).mock(return_value=httpx.Response(200, json=fake_api_response))

    # 2. ACT (Uruchamiamy naszą prawdziwą funkcję)
    result = await fetch_items()

    # 3. ASSERT (Sprawdzamy wynik)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["market_hash_name"] == "AK-47 | Redline (Field-Tested)"


# TEST 2: Sprawdzamy reakcję na błąd ze Skinportu (np. blokada limitu 429)
@pytest.mark.asyncio
@respx.mock
async def test_fetch_items_http_error():
    # 1. ARRANGE (Udajemy, że Skinport zwraca błąd 429 Too Many Requests)
    respx.get(URL).mock(return_value=httpx.Response(429))

    # 2. ACT & ASSERT (Oczekujemy, że funkcja rzuci wyjątek HTTPStatusError)
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_items()
