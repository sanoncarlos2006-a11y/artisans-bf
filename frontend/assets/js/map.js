(function () {
  const defaultCenter = [12.3714, -1.5197];

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
              `<li><span>${business.name}</span><small>${business.latitude}, ${business.longitude}</small></li>`
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

    businesses.forEach((business) => {
      if (!business.latitude || !business.longitude) return;
      L.marker([Number(business.latitude), Number(business.longitude)])
        .addTo(map)
        .bindPopup(
          `<strong>${business.name}</strong><br>${business.category}<br>${
            business.address_description || ""
          }`
        );
    });

    window.setTimeout(() => map.invalidateSize(), 120);
    return map;
  }

  window.MapView = { render };
})();
