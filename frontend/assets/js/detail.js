(function () {
  let business = null;

  function safeExternalUrl(url) {
    return url || "#";
  }

  function getPosition(options = {}) {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocalisation non disponible."));
        return;
      }
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: false,
        timeout: 12000,
        maximumAge: 60000,
        ...options
      });
    });
  }

  function commentsPanel() {
    return window.UI.qs("[data-comments-panel]");
  }

  function scrollToComments() {
    const panel = commentsPanel();
    if (!panel) return;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function openRoute() {
    let url = business.google_navigation_url || business.google_maps_url;
    try {
      const position = await getPosition();
      url = window.Api.googleMapsNavigationUrl(business, {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      });
    } catch (error) {
      window.UI.toast("Itineraire ouvert sans position de depart precise.", "warning");
    }
    if (url) window.open(url, "_blank", "noopener,noreferrer");
  }

  async function refreshComments() {
    try {
      business.comments = await window.Api.listComments(business.id);
    } catch (error) {
      business.comments = business.comments || [];
    }
  }

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

  function ratingSummary(comments) {
    const ratings = comments
      .map((comment) => Number(comment.rating))
      .filter((rating) => !Number.isNaN(rating) && rating > 0);
    if (!ratings.length) return { rating_average: 0, rating_count: 0 };
    return {
      rating_average: ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length,
      rating_count: ratings.length
    };
  }

  function mergeSubmittedComment(latestBusiness, submittedComment) {
    const currentComments = latestBusiness.comments || [];
    if (!submittedComment) return { ...latestBusiness, comments: currentComments };

    const exists = currentComments.some(
      (comment) => String(comment.id || "") === String(submittedComment.id || "")
    );
    const comments = exists ? currentComments : [submittedComment, ...currentComments];
    const summary = comments.length ? ratingSummary(comments) : {};
    return { ...latestBusiness, ...summary, comments };
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
    window.UI.qs("[data-google-maps]").href = safeExternalUrl(business.google_maps_url);

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
        <a class="business-photo detail-tile" data-detail-action="maps" target="_blank" rel="noreferrer" href="${window.UI.escapeHtml(
          safeExternalUrl(business.google_maps_url)
        )}">
          <strong>Carte</strong>
          <small>Ouvrir Google Maps</small>
        </a>
        <button class="business-photo detail-tile" data-detail-action="route" type="button">
          <strong>GPS</strong>
          <small>Demarrer l'itineraire</small>
        </button>
        <button class="business-photo detail-tile" data-detail-action="comments" type="button">
          <strong>${window.UI.escapeHtml(window.UI.formatRating(business.rating_average, business.rating_count))}</strong>
          <small>Voir les avis</small>
        </button>
      `;

    if (window.MapView) {
      window.MapView.render("detail-map", [business], { zoom: 15 });
    }
    renderComments();
    bindDetailActions();
  }

  function bindDetailActions() {
    const routeButton = window.UI.qs("[data-google-route]");
    if (routeButton) routeButton.onclick = openRoute;

    window.UI.qsa("[data-detail-action='route']").forEach((button) => {
      button.onclick = openRoute;
    });
    window.UI.qsa("[data-detail-action='comments']").forEach((button) => {
      button.onclick = scrollToComments;
    });
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
        const fallbackComments = [response.comment, ...(business.comments || [])].filter(Boolean);
        try {
          const latestBusiness = await window.Api.businessDetail(business.id);
          business = mergeSubmittedComment(latestBusiness, response.comment);
        } catch (error) {
          business = {
            ...business,
            ...(response.business || {}),
            ...ratingSummary(fallbackComments),
            comments: fallbackComments
          };
        }
        window.UI.toast("Avis ajoute, la note du commerce est mise a jour.");
        form.reset();
        renderDetail();
        scrollToComments();
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
      business = await window.Api.businessDetail(id);
      if (!business) throw new Error("Commerce introuvable ou non publie.");
      await refreshComments();
      renderDetail();
      initCommentForm();
    } catch (error) {
      window.UI.toast(error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
