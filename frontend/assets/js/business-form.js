(function () {
  function isLocalHost() {
    return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
  }

  function canAskBrowserLocation() {
    return Boolean(navigator.geolocation) && (window.isSecureContext || isLocalHost());
  }

  function locationErrorMessage(error) {
    if (!window.isSecureContext && !isLocalHost()) {
      return "GPS bloque: ouvre le site en HTTPS ou sur localhost.";
    }
    if (!error) return "Geolocalisation non disponible sur ce navigateur.";
    if (error.code === error.PERMISSION_DENIED) {
      return "Position refusee. Autorise la localisation dans le navigateur.";
    }
    if (error.code === error.TIMEOUT) {
      return "Position trop lente. Tu peux saisir latitude et longitude.";
    }
    return "Impossible de lire la position GPS. Tu peux saisir latitude et longitude.";
  }

  function readNumberField(form, name) {
    const value = form.elements[name].value;
    return value === "" ? null : Number(value);
  }

  function initGeoButton() {
    const button = window.UI.qs("[data-use-location]");
    const form = window.UI.qs("[data-business-form]");
    if (!button || !form) return;

    button.addEventListener("click", () => {
      if (!canAskBrowserLocation()) {
        window.UI.toast(locationErrorMessage(), "warning");
        return;
      }
      button.disabled = true;
      navigator.geolocation.getCurrentPosition(
        (position) => {
          form.elements.latitude.value = position.coords.latitude.toFixed(6);
          form.elements.longitude.value = position.coords.longitude.toFixed(6);
          window.UI.toast("Position GPS ajoutee.");
          button.disabled = false;
        },
        (error) => {
          window.UI.toast(locationErrorMessage(error), "error");
          button.disabled = false;
        },
        { enableHighAccuracy: false, timeout: 15000, maximumAge: 60000 }
      );
    });
  }

  function initForm() {
    const form = window.UI.qs("[data-business-form]");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        const data = window.UI.formDataObject(form);
        const payload = {
          name: data.name,
          category: data.category,
          phone: data.phone,
          opening_hours: data.opening_hours,
          address_description: data.address_description,
          description: data.description,
          latitude: readNumberField(form, "latitude"),
          longitude: readNumberField(form, "longitude")
        };
        const business = await window.Api.createBusiness(payload);
        const files = form.elements.photos.files;
        if (files && files.length) {
          await window.Api.uploadPhotos(business.id, files);
        }
        window.UI.toast("Commerce cree en brouillon.");
        window.location.href = "dashboard.html";
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  async function init() {
    const user = await window.UI.requireAuth();
    if (!user) return;
    initGeoButton();
    initForm();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
