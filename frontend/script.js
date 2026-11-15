const API_URL = "http://127.0.0.1:8000/items";
let allItems = [];

async function loadItems() {
    const container = document.getElementById("items");

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("Nie udało się pobrać danych");

        allItems = await response.json();
        applyFilters();
    } catch (error) {
        container.innerHTML = `<p style="color: #ff6b6b;">Błąd: ${error.message}</p>`;
    }
}

function renderItems(items) {
    const container = document.getElementById("items");
    container.innerHTML = "";

    if (items.length === 0) {
        container.innerHTML = "<p>Brak skinów pasujących do wyszukiwania.</p>";
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

function applyFilters() {
    const searchTerm = document.getElementById("search").value.toLowerCase();
    const sortCriteria = document.getElementById("sort").value;

    let filtered = allItems.filter(item =>
        item.name.toLowerCase().includes(searchTerm)
    );

    switch (sortCriteria) {
        case "name-asc":
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case "name-desc":
            filtered.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case "price-asc":
            filtered.sort((a, b) => a.price - b.price);
            break;
        case "price-desc":
            filtered.sort((a, b) => b.price - a.price);
            break;
    }

    renderItems(filtered);
}

document.getElementById("search").addEventListener("input", applyFilters);
document.getElementById("sort").addEventListener("change", applyFilters);

loadItems();