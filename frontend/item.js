const params = new URLSearchParams(window.location.search);
const itemId = params.get("id");

function getImageUrl(marketHashName) {
    if (!marketHashName) return "https://via.placeholder.com/200x150?text=Brak+obrazka";
    // Przykładowy serwis (może wymagać klucza lub mieć limity)
    return `https://api.steamapis.com/image/item/730/${encodeURIComponent(marketHashName)}`;
}

function getImageUrl(marketHashName) {
    if (!marketHashName) {
        return "https://via.placeholder.com/200x150?text=Brak+obrazka";
    }
    // Przykładowe źródło (możesz później zmienić na inne)
    return `https://api.steamapis.com/image/item/730/${encodeURIComponent(marketHashName)}`;
}

async function loadItem() {
    const container = document.getElementById("item-details");

    if (!itemId) {
        container.innerHTML = "<p>Nie podano ID skina.</p>";
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/items/${itemId}`);
        if (!response.ok) throw new Error("Nie udało się pobrać danych");

        const item = await response.json();

        container.innerHTML = `
            <div class="item-detail-card">
                <h1>${item.market_hash_name}</h1>
                <img src="${getImageUrl(item.market_hash_name)}" alt="${item.market_hash_name}" class="item-detail-image"loading="lazy">
                <p class="rarity">${item.version || "—"}</p>
                <p class="price">${item.min_price ?? "—"} ${item.currency || "PLN"}</p>
                <p><strong>Sugerowana cena:</strong> ${item.suggested_price ?? "—"}</p>
                <p><strong>Min. cena:</strong> ${item.min_price ?? "—"}</p>
                <p><strong>Max. cena:</strong> ${item.max_price ?? "—"}</p>
                <p><strong>Średnia cena:</strong> ${item.mean_price ?? "—"}</p>
                <p><strong>Mediana:</strong> ${item.median_price ?? "—"}</p>
                <p><strong>Ilość:</strong> ${item.quantity ?? "—"}</p>
                <p><strong>Waluta:</strong> ${item.currency || "—"}</p>
                ${item.item_page ? `<p><a href="${item.item_page}" target="_blank">Zobacz na Skinport</a></p>` : ""}
                ${item.market_page ? `<p><a href="${item.market_page}" target="_blank">Strona marketu</a></p>` : ""}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p style="color: #ff6b6b;">Błąd: ${error.message}</p>`;
    }
}

loadItem();