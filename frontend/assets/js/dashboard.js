(function () {
  let businesses = [];

  function counts() {
    const total = businesses.length;
    const published = businesses.filter((business) => business.status === "published")
      .length;
    const draft = total - published;
    window.UI.qs("[data-count-total]").textContent = total;
    window.UI.qs("[data-count-published]").textContent = published;
    window.UI.qs("[data-count-draft]").textContent = draft;
  }

  function render() {
    const list = window.UI.qs("[data-dashboard-list]");
    if (!list) return;

    counts();

    if (!businesses.length) {
      list.innerHTML = `
        <div class="empty-state">
          <div>
            <strong>Aucun commerce enregistre</strong>
            <p>Ajoute ton premier atelier, commerce ou service pour le preparer en brouillon.</p>
          </div>
        </div>
      `;
      return;
    }

    list.innerHTML = businesses
      .map((business) =>
        window.UI.businessCard(business, {
          showStatus: true,
          actions: `
            <button class="button ${
              business.status === "published" ? "button-danger" : ""
            }" data-toggle-publish="${business.id}">
              ${business.status === "published" ? "Retirer" : "Publier"}
            </button>
          `
        })
      )
      .join("");

    window.UI.qsa("[data-toggle-publish]", list).forEach((button) => {
      button.addEventListener("click", async () => {
        const id = button.dataset.togglePublish;
        const business = businesses.find((item) => String(item.id) === String(id));
        button.disabled = true;
        try {
          const updated =
            business.status === "published"
              ? await window.Api.unpublishBusiness(id)
              : await window.Api.publishBusiness(id);
          businesses = businesses.map((item) =>
            String(item.id) === String(id) ? updated : item
          );
          window.UI.toast(
            updated.status === "published"
              ? "Commerce publie dans l'annuaire."
              : "Commerce retire de l'annuaire public."
          );
          render();
        } catch (error) {
          window.UI.toast(error.message, "error");
        } finally {
          button.disabled = false;
        }
      });
    });
  }

  async function init() {
    const user = await window.UI.requireAuth();
    if (!user) return;
    try {
      businesses = await window.Api.myBusinesses();
      render();
    } catch (error) {
      window.UI.toast(error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
