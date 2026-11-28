const params = new URLSearchParams(window.location.search);
const itemId = params.get("id");

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
                <h1>${item.name}</h1>
                <p class="rarity">${item.rarity || "Brak rarity"}</p>
                <p class="price">$${item.price}</p>
                <p><strong>Min. cena:</strong> ${item.min_price ?? "—"}</p>
                <p><strong>Max. cena:</strong> ${item.max_price ?? "—"}</p>
                <p><strong>Ilość:</strong> ${item.quantity ?? "—"}</p>
                <p><strong>Waluta:</strong> ${item.currency || "—"}</p>
                ${item.item_page ? `<p><a href="${item.item_page}" target="_blank">Zobacz na Skinport</a></p>` : ""}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p style="color: #ff6b6b;">Błąd: ${error.message}</p>`;
    }
}

loadItem();