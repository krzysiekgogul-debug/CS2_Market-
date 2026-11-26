const API_URL = "http://127.0.0.1:8000/skins_from_db";
const searchInput = document.getElementById("item-search");
const suggestionsBox = document.getElementById("suggestions");

function getImageUrl(item) {
    return item.image_url || "https://via.placeholder.com/200x150?text=Brak+obrazka";
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
                <img src="${getImageUrl(item)}" alt="${item.market_hash_name}" class="item-image" loading="lazy" onerror="this.src='https://via.placeholder.com/200x150?text=Brak+obrazka'">
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

searchInput.addEventListener("input", async () => {
    const query = searchInput.value.trim();
    suggestionsBox.innerHTML = "";

    if (query.length < 2) return;

    try {
        const response = await fetch(`http://127.0.0.1:8000/items/suggestions?q=${encodeURIComponent(query)}`);
        const suggestions = await response.json();

        suggestions.forEach(name => {
            const div = document.createElement("div");
            div.textContent = name;
            div.style.padding = "8px";
            div.style.cursor = "pointer";
            div.style.color = "#ffcc00";
            div.addEventListener("click", () => {
                searchInput.value = name;
                suggestionsBox.innerHTML = "";
            });
            suggestionsBox.appendChild(div);
        });
    } catch (error) {
        console.error("Błąd podpowiedzi");
    }
});

document.getElementById("search-btn").addEventListener("click", async () => {
    const name = document.getElementById("item-search").value.trim();
    if (!name) return;

    try {
        const response = await fetch(`http://127.0.0.1:8000/items/search?name=${encodeURIComponent(name)}`);
        const data = await response.json();

        if (data.error) {
            alert("Nie znaleziono skina");
            return;
        }

        window.location.href = `item.html?id=${data.id}`;
    } catch (error) {
        alert("Błąd wyszukiwania");
    }
});