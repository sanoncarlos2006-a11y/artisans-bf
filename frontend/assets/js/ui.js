(function () {
  const categorySelects = [];

  function qs(selector, root = document) {
    return root.querySelector(selector);
  }

  function qsa(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
  }

  function toast(message, type = "info") {
    let region = qs("[data-toast-region]");
    if (!region) {
      region = document.createElement("div");
      region.className = "toast-region";
      region.setAttribute("data-toast-region", "");
      document.body.appendChild(region);
    }

    const item = document.createElement("div");
    item.className = `toast toast-${type}`;
    item.textContent = message;
    region.appendChild(item);

    window.setTimeout(() => {
      item.classList.add("toast-out");
      window.setTimeout(() => item.remove(), 220);
    }, 4200);
  }

  function setLoading(form, isLoading) {
    const button = qs("[type='submit']", form);
    if (!button) return;
    button.disabled = isLoading;
    button.dataset.originalText = button.dataset.originalText || button.textContent;
    button.textContent = isLoading ? "Traitement..." : button.dataset.originalText;
  }

  function formatRating(value, count) {
    const rating = Number(value || 0);
    if (!rating) return "Pas encore note";
    const rounded = rating.toFixed(1);
    return `${rounded}/5${count ? ` (${count})` : ""}`;
  }

  function distanceLabel(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "Distance non calculee";
    }
    const distance = Number(value);
    if (distance < 1) return `${Math.round(distance * 1000)} m`;
    return `${distance.toFixed(1)} km`;
  }

  function escapeHtml(value) {
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

  function businessPhoto(business) {
    if (business.photos && business.photos.length) {
      return `<img src="${escapeHtml(business.photos[0])}" alt="${escapeHtml(
        business.name
      )}">`;
    }
    const category = escapeHtml(
      String(business.category || "Service").slice(0, 2).toUpperCase()
    );
    return `<div class="photo-fallback" aria-hidden="true">${category}</div>`;
  }

  function businessCard(business, options = {}) {
    const detailUrl = `business-detail.html?id=${encodeURIComponent(business.id)}`;
    const statusClass =
      business.status === "published" ? "status-published" : "status-draft";
    const actions = options.actions || "";
    return `
      <article class="business-card" data-business-id="${escapeHtml(business.id)}">
        <a class="business-photo" href="${detailUrl}">
          ${businessPhoto(business)}
        </a>
        <div class="business-content">
          <div class="business-topline">
            <span class="pill">${escapeHtml(business.category || "Service")}</span>
            ${
              options.showStatus
                ? `<span class="status ${statusClass}">${
                    business.status === "published" ? "Publie" : "Brouillon"
                  }</span>`
                : ""
            }
          </div>
          <h3><a href="${detailUrl}">${escapeHtml(business.name)}</a></h3>
          <p>${escapeHtml(business.address_description || "Adresse a completer")}</p>
          <div class="business-meta">
            <span>${formatRating(business.rating_average, business.rating_count)}</span>
            <span>${distanceLabel(business.distance_km)}</span>
            <span>${escapeHtml(
              business.opening_hours || "Horaires non renseignes"
            )}</span>
          </div>
          <div class="business-actions">
            <a class="button button-secondary" href="tel:${escapeHtml(
              business.phone || ""
            )}">Appeler</a>
            <a class="button button-secondary" target="_blank" rel="noreferrer" href="${whatsAppUrl(
              business
            )}">WhatsApp</a>
            ${actions}
          </div>
        </div>
      </article>
    `;
  }

  function whatsAppUrl(business) {
    const text = [
      `Bonjour, je vous contacte depuis Annuaire Artisans BF.`,
      `Commerce: ${business.name}`,
      `Categorie: ${business.category}`,
      business.address_description ? `Adresse: ${business.address_description}` : "",
      business.phone ? `Telephone: ${business.phone}` : ""
    ]
      .filter(Boolean)
      .join("\n");
    const phone = String(business.phone || "").replace(/[^\d]/g, "");
    return `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
  }

  function fillCategorySelects() {
    categorySelects.push(...qsa("[data-category-select]"));
    categorySelects.forEach((select) => {
      const selected = select.dataset.selected || select.value;
      const first = select.dataset.emptyLabel || "Toutes les categories";
      select.innerHTML = `<option value="">${first}</option>${window.AppConfig.categories
        .map(
          (category) =>
            `<option value="${category}" ${
              selected === category ? "selected" : ""
            }>${category}</option>`
        )
        .join("")}`;
    });
  }

  function setActiveNav() {
    const page = document.body.dataset.page;
    qsa("[data-nav]").forEach((link) => {
      if (link.dataset.nav === page) link.setAttribute("aria-current", "page");
    });
  }

  async function requireAuth() {
    try {
      return await window.Api.me();
    } catch (error) {
      toast("Connecte-toi pour acceder a cette page.", "warning");
      window.setTimeout(() => {
        window.location.href = "login.html";
      }, 700);
      return null;
    }
  }

  function initAuthLinks() {
    const user = window.Api.currentUser();
    qsa("[data-user-name]").forEach((node) => {
      node.textContent = user ? user.full_name || user.phone : "Invite";
    });
    qsa("[data-auth-only]").forEach((node) => {
      node.hidden = !user;
    });
    qsa("[data-guest-only]").forEach((node) => {
      node.hidden = Boolean(user);
    });
    qsa("[data-logout]").forEach((button) => {
      button.addEventListener("click", () => {
        window.Api.clearSession();
        toast("Session fermee.");
        window.location.href = "index.html";
      });
    });
  }

  function formDataObject(form) {
    const data = new FormData(form);
    return Object.fromEntries(data.entries());
  }

  function initApiSettings() {
    const input = qs("[data-api-base-url]");
    if (!input) return;
    input.value = window.AppConfig.apiBaseUrl;
    input.addEventListener("change", () => {
      localStorage.setItem("annuaire_api_base_url", input.value.trim());
      window.AppConfig.apiBaseUrl = input.value.trim();
      toast("URL API mise a jour.");
    });
  }

  function init() {
    fillCategorySelects();
    setActiveNav();
    initAuthLinks();
    initApiSettings();
  }

  document.addEventListener("DOMContentLoaded", init);

  window.UI = {
    qs,
    qsa,
    toast,
    setLoading,
    formatRating,
    distanceLabel,
    escapeHtml,
    businessCard,
    whatsAppUrl,
    requireAuth,
    formDataObject
  };
})();
