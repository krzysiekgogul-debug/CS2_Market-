const API_URL = "http://127.0.0.1:8000/items";
let allItems = [];

async function loadItems() {
    const container = document.getElementById("items");

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("Nie udało się pobrać danych");

        allItems = await response.json();
        renderItems(allItems);
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
            <h3>${item.name}</h3>
            <p class="rarity">${item.rarity || "Brak rarity"}</p>
            <p class="price">$${item.price}</p>
        `;
        container.appendChild(card);
    });
}

function sortItems(criteria) {
    const sorted = [...allItems];

    switch (criteria) {
        case "name-asc":
            sorted.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case "name-desc":
            sorted.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case "price-asc":
            sorted.sort((a, b) => a.price - b.price);
            break;
        case "price-desc":
            sorted.sort((a, b) => b.price - a.price);
            break;
    }

    renderItems(sorted);
}

document.getElementById("sort").addEventListener("change", (e) => {
    sortItems(e.target.value);
});

loadItems();