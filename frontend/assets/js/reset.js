(function () {
  function initForgotForm() {
    const form = window.UI.qs("[data-forgot-form]");
    const codeBox = window.UI.qs("[data-reset-code]");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        const payload = await window.Api.forgotPassword(window.UI.formDataObject(form));
        const code = payload.reset_code || payload.code || "code envoye";
        if (codeBox) {
          codeBox.hidden = false;
          codeBox.textContent = `Code de test: ${code}`;
        }
        window.UI.toast("Code reset genere.");
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  function initResetForm() {
    const form = window.UI.qs("[data-reset-form]");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        await window.Api.resetPassword(window.UI.formDataObject(form));
        window.UI.toast("Mot de passe modifie.");
        window.location.href = "login.html";
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initForgotForm();
    initResetForm();
  });
})();
