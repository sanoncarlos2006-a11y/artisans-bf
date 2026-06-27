(function () {
  let currentPosition = null;
  let currentResults = [];

  function isValidCoordinate(latitude, longitude) {
    return (
      !Number.isNaN(latitude) &&
      !Number.isNaN(longitude) &&
      latitude >= -90 &&
      latitude <= 90 &&
      longitude >= -180 &&
      longitude <= 180
    );
  }

  function isLocalHost() {
    return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
  }

  function canAskBrowserLocation() {
    return Boolean(navigator.geolocation) && (window.isSecureContext || isLocalHost());
  }

  function revealManualLocationFields() {
    window.UI.qsa("[data-location-fields]").forEach((node) => {
      node.hidden = false;
    });
  }

  function locationErrorMessage(error) {
    if (!window.isSecureContext && !isLocalHost()) {
      return "GPS bloque: ouvre le site en HTTPS ou sur localhost.";
    }
    if (!error) return "Position GPS indisponible.";
    if (error.code === error.PERMISSION_DENIED) {
      return "Position refusee. Autorise la localisation dans le navigateur.";
    }
    if (error.code === error.TIMEOUT) {
      return "Position trop lente. Saisis latitude et longitude manuellement.";
    }
    return "Position GPS indisponible. Saisis latitude et longitude manuellement.";
  }

  function readSearchPosition(form) {
    const latRaw = form.elements.lat ? form.elements.lat.value.trim() : "";
    const lngRaw = form.elements.lng ? form.elements.lng.value.trim() : "";
    if (!latRaw || !lngRaw) return currentPosition;

    const lat = Number(latRaw);
    const lng = Number(lngRaw);
    if (isValidCoordinate(lat, lng)) {
      return { latitude: lat, longitude: lng };
    }
    return currentPosition;
  }

  function writeManualPosition(form, position) {
    if (!form.elements.lat || !form.elements.lng) return;
    form.elements.lat.value = position.latitude.toFixed(6);
    form.elements.lng.value = position.longitude.toFixed(6);
  }

  function paramsFromForm(form) {
    const data = window.UI.formDataObject(form);
    const position = readSearchPosition(form);
    const params = {
      q: data.q,
      category: data.category,
      min_rating: data.min_rating
    };
    if (position) {
      params.lat = position.latitude;
      params.lng = position.longitude;
    }
    return params;
  }

  function renderResults(results, position) {
    currentResults = results;
    const list = window.UI.qs("[data-results-list]");
    const count = window.UI.qs("[data-results-count]");
    if (count) count.textContent = `${results.length} resultat(s)`;

    if (!list) return;
    if (!results.length) {
      list.innerHTML = `
        <div class="empty-state">
          <div>
            <strong>Aucun resultat</strong>
            <p>Change la categorie, la note minimale ou lance la recherche sans proximite.</p>
          </div>
        </div>
      `;
    } else {
      list.innerHTML = results.map((business) => window.UI.businessCard(business)).join("");
    }

    if (window.MapView) {
      window.MapView.render("map", results, {
        center: position
          ? [position.latitude, position.longitude]
          : undefined
      });
    }
  }

  async function runSearch(form) {
    try {
      const position = readSearchPosition(form);
      const results = await window.Api.searchBusinesses(paramsFromForm(form));
      renderResults(results, position);
    } catch (error) {
      window.UI.toast(error.message, "error");
    }
  }

  function initLocationButton(form) {
    const button = window.UI.qs("[data-search-location]");
    if (!button) return;
    button.addEventListener("click", () => {
      if (!canAskBrowserLocation()) {
        revealManualLocationFields();
        window.UI.toast(locationErrorMessage(), "warning");
        return;
      }
      button.disabled = true;
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          currentPosition = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          revealManualLocationFields();
          writeManualPosition(form, currentPosition);
          window.UI.toast("Recherche par proximite activee.");
          button.disabled = false;
          await runSearch(form);
        },
        (error) => {
          revealManualLocationFields();
          button.disabled = false;
          window.UI.toast(locationErrorMessage(error), "error");
        },
        { enableHighAccuracy: false, timeout: 15000, maximumAge: 60000 }
      );
    });
  }

  function initSearch() {
    const form = window.UI.qs("[data-search-form]");
    if (!form) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      await runSearch(form);
      window.UI.setLoading(form, false);
    });

    initLocationButton(form);
    runSearch(form);
  }

  document.addEventListener("DOMContentLoaded", initSearch);
})();
