(function () {
  function initLogin() {
    const form = window.UI.qs("[data-login-form]");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        await window.Api.login(window.UI.formDataObject(form));
        window.UI.toast("Connexion reussie.");
        window.location.href = "dashboard.html";
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  function initRegister() {
    const form = window.UI.qs("[data-register-form]");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        await window.Api.register(window.UI.formDataObject(form));
        window.UI.toast("Compte cree. Bienvenue.");
        window.location.href = "dashboard.html";
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLogin();
    initRegister();
  });
})();
