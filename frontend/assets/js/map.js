(function () {
  const defaultCenter = [12.3714, -1.5197];

  function escapePopup(value) {
    if (window.UI && window.UI.escapeHtml) return window.UI.escapeHtml(value);
    return String(value ?? "").replace(/[&<>"']/g, (character) => {
      const entities = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      };
      return entities[character];
    });
  }

  function mapFallback(container, businesses) {
    container.classList.add("map-fallback-panel");
    container.innerHTML = `
      <div>
        <strong>Carte indisponible</strong>
        <p>Les coordonnees GPS restent affichees pour garder le test lisible.</p>
      </div>
      <ul>
        ${businesses
          .map(
            (business) =>
              `<li><span>${escapePopup(business.name)}</span><small>${escapePopup(
                `${business.latitude}, ${business.longitude}`
              )}</small></li>`
          )
          .join("")}
      </ul>
    `;
  }

  function render(containerId, businesses = [], options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return null;

    if (!window.L) {
      mapFallback(container, businesses);
      return null;
    }

    container.innerHTML = "";
    const centerBusiness = businesses.find(
      (business) => business.latitude && business.longitude
    );
    const center = options.center ||
      (centerBusiness
        ? [Number(centerBusiness.latitude), Number(centerBusiness.longitude)]
        : defaultCenter);
    const map = L.map(container).setView(center, options.zoom || 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap"
    }).addTo(map);

    if (options.center) {
      L.circleMarker(options.center, {
        radius: 8,
        color: "#0f5132",
        fillColor: "#146c43",
        fillOpacity: 0.9,
        weight: 3
      })
        .addTo(map)
        .bindPopup("Votre position");
    }

    businesses.forEach((business) => {
      if (!business.latitude || !business.longitude) return;
      const routeUrl =
        business.google_navigation_url || business.google_maps_url || business.openstreetmap_url || "#";
      L.marker([Number(business.latitude), Number(business.longitude)])
        .addTo(map)
        .bindPopup(
          `<strong>${escapePopup(business.name)}</strong><br>${escapePopup(
            business.category
          )}<br>${escapePopup(
            business.address_description || ""
          )}<br><a target="_blank" rel="noreferrer" href="${escapePopup(
            routeUrl
          )}">Ouvrir l'itineraire</a>`
        );
    });

    window.setTimeout(() => map.invalidateSize(), 120);
    return map;
  }

  window.MapView = { render };
})();
