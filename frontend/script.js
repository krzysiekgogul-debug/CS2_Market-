const API_URL = "http://127.0.0.1:8000/skins_from_db";

function getImageUrl(marketHashName) {
    if (!marketHashName) {
        return "https://via.placeholder.com/200x150?text=Brak+obrazka";
    }
    // Przykładowe źródło (możesz później zmienić na inne)
    return `https://api.steamapis.com/image/item/730/${encodeURIComponent(marketHashName)}`;
}

async function loadItems() {
    const container = document.getElementById("items");

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("Nie udało się pobrać danych");

        const items = await response.json();
        renderItems(items);
    } catch (error) {
        container.innerHTML = `<p style="color: #ff6b6b;">Błąd: ${error.message}</p>`;
    }
}

function renderItems(items) {
    const container = document.getElementById("items");
    container.innerHTML = "";

    if (items.length === 0) {
        container.innerHTML = "<p>Brak skinów.</p>";
        return;
    }

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "item-card";
        card.innerHTML = `
            <a href="item.html?id=${item.id}" class="card-link">
                <img src="${getImageUrl(item.market_hash_name)}" alt="${item.market_hash_name}" class="item-image" loading="lazy" onerror="this.src='https://via.placeholder.com/200x150?text=Brak+obrazka'">
                <h3>${item.market_hash_name}</h3>
                <p class="rarity">${item.version || "—"}</p>
                <p class="price">${item.min_price ?? "—"} ${item.currency || "PLN"}</p>
            </a>
        `;
        container.appendChild(card);
    });
}

loadItems();

document.getElementById("refresh-btn").addEventListener("click", () => {
    loadItems();
});