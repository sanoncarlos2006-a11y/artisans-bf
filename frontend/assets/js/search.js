(function () {
  let currentPosition = null;
  let currentResults = [];

  function paramsFromForm(form) {
    const data = window.UI.formDataObject(form);
    const params = {
      q: data.q,
      category: data.category,
      min_rating: data.min_rating
    };
    if (currentPosition) {
      params.lat = currentPosition.latitude;
      params.lng = currentPosition.longitude;
    }
    return params;
  }

  function renderResults(results) {
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
        center: currentPosition
          ? [currentPosition.latitude, currentPosition.longitude]
          : undefined
      });
    }
  }

  async function runSearch(form) {
    try {
      const results = await window.Api.searchBusinesses(paramsFromForm(form));
      renderResults(results);
    } catch (error) {
      window.UI.toast(error.message, "error");
    }
  }

  function initLocationButton(form) {
    const button = window.UI.qs("[data-search-location]");
    if (!button) return;
    button.addEventListener("click", () => {
      if (!navigator.geolocation) {
        window.UI.toast("Geolocalisation non disponible.", "warning");
        return;
      }
      button.disabled = true;
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          currentPosition = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          window.UI.toast("Recherche par proximite activee.");
          button.disabled = false;
          await runSearch(form);
        },
        () => {
          button.disabled = false;
          window.UI.toast("Position GPS indisponible.", "error");
        },
        { enableHighAccuracy: true, timeout: 9000 }
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
