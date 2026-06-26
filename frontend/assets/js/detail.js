(function () {
  let business = null;

  function renderComments() {
    const list = window.UI.qs("[data-comments-list]");
    if (!list) return;
    const comments = business.comments || [];
    if (!comments.length) {
      list.innerHTML = `<div class="empty-state">Aucun commentaire pour le moment.</div>`;
      return;
    }
    list.innerHTML = comments
      .map(
        (comment) => `
          <article class="comment">
            <strong>${window.UI.escapeHtml(comment.author_name || "Client")} - ${window.UI.escapeHtml(
              comment.rating || ""
            )}/5</strong>
            <p>${window.UI.escapeHtml(comment.content || "")}</p>
            <small>${window.UI.escapeHtml(comment.justification || "")}</small>
          </article>
        `
      )
      .join("");
  }

  function renderDetail() {
    document.title = `${business.name} - Annuaire Artisans BF`;
    window.UI.qs("[data-business-name]").textContent = business.name;
    window.UI.qs("[data-business-category]").textContent = business.category;
    window.UI.qs("[data-business-rating]").textContent = window.UI.formatRating(
      business.rating_average,
      business.rating_count
    );
    window.UI.qs("[data-business-address]").textContent =
      business.address_description || "Adresse non renseignee";
    window.UI.qs("[data-business-hours]").textContent =
      business.opening_hours || "Horaires non renseignes";
    window.UI.qs("[data-business-description]").textContent =
      business.description || "Description a completer.";
    window.UI.qs("[data-call]").href = `tel:${business.phone || ""}`;
    window.UI.qs("[data-whatsapp]").href = window.UI.whatsAppUrl(business);

    const photos = window.UI.qs("[data-photo-strip]");
    const photoItems = business.photos && business.photos.length ? business.photos : [];
    photos.innerHTML = photoItems.length
      ? photoItems
          .slice(0, 3)
          .map(
            (photo) =>
              `<div class="business-photo"><img src="${window.UI.escapeHtml(
                photo
              )}" alt="${window.UI.escapeHtml(business.name)}"></div>`
          )
          .join("")
      : `
        <div class="business-photo"><div class="photo-fallback">BF</div></div>
        <div class="business-photo"><div class="photo-fallback">GPS</div></div>
        <div class="business-photo"><div class="photo-fallback">5/5</div></div>
      `;

    if (window.MapView) {
      window.MapView.render("detail-map", [business], { zoom: 15 });
    }
    renderComments();
  }

  function initCommentForm() {
    const form = window.UI.qs("[data-comment-form]");
    if (!form) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      window.UI.setLoading(form, true);
      try {
        const payload = window.UI.formDataObject(form);
        const response = await window.Api.addComment(business.id, payload);
        business = response.business || {
          ...business,
          comments: [response.comment, ...(business.comments || [])]
        };
        window.UI.toast("Avis ajoute, la note du commerce est mise a jour.");
        form.reset();
        renderDetail();
      } catch (error) {
        window.UI.toast(error.message, "error");
      } finally {
        window.UI.setLoading(form, false);
      }
    });
  }

  async function init() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (!id) {
      window.UI.toast("Identifiant commerce manquant.", "error");
      window.location.href = "search.html";
      return;
    }

    try {
      business = await window.Api.findBusiness(id);
      if (!business) throw new Error("Commerce introuvable ou non publie.");
      renderDetail();
      initCommentForm();
    } catch (error) {
      window.UI.toast(error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
