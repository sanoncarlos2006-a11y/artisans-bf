(function () {
  const storeKey = "annuaire_demo_store_v1";

  function uid(prefix) {
    return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  }

  function normalizeText(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function distanceKm(lat1, lon1, lat2, lon2) {
    if ([lat1, lon1, lat2, lon2].some((value) => Number.isNaN(Number(value)))) {
      return null;
    }

    const toRad = (value) => (Number(value) * Math.PI) / 180;
    const earthRadius = 6371;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) *
        Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    return earthRadius * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function keywordRating(comment) {
    const text = normalizeText(comment);
    const positives = [
      "rapide",
      "propre",
      "professionnel",
      "bon",
      "excellent",
      "satisfait",
      "merci",
      "qualite",
      "recommande"
    ];
    const negatives = [
      "retard",
      "cher",
      "mauvais",
      "sale",
      "mal",
      "lent",
      "decu",
      "probleme",
      "impoli"
    ];
    const score =
      positives.filter((word) => text.includes(word)).length -
      negatives.filter((word) => text.includes(word)).length;

    if (score >= 3) return { rating: 5, justification: "Avis tres positif" };
    if (score >= 1) return { rating: 4, justification: "Avis positif" };
    if (score === 0) return { rating: 3, justification: "Avis neutre" };
    if (score === -1) return { rating: 2, justification: "Avis negatif" };
    return { rating: 1, justification: "Avis tres negatif" };
  }

  function defaultStore() {
    return {
      users: [
        {
          id: "user_demo",
          full_name: "Compte demo",
          phone: "+22670000000",
          password: "demo1234"
        }
      ],
      resetCodes: {},
      businesses: [
        {
          id: "biz_couture",
          owner_id: "user_demo",
          name: "Atelier Kadi Couture",
          category: "Couturier",
          phone: "+22670000001",
          opening_hours: "Lun-Sam, 08h00-18h30",
          address_description: "Ouagadougou, 1200 logements, pres du marche",
          description:
            "Retouches, tenues traditionnelles et commandes rapides pour femmes, hommes et enfants.",
          latitude: 12.3714,
          longitude: -1.5197,
          status: "published",
          photos: [],
          rating_average: 4.7,
          rating_count: 12,
          comments: [
            {
              id: "com_1",
              author_name: "Awa",
              content: "Travail rapide, propre et professionnel.",
              rating: 5,
              justification: "Avis tres positif",
              created_at: "2026-06-20"
            }
          ]
        },
        {
          id: "biz_moto",
          owner_id: "user_demo",
          name: "Garage Wend-Panga Moto",
          category: "Mecanicien",
          phone: "+22670000002",
          opening_hours: "Tous les jours, 07h30-19h00",
          address_description: "Bobo-Dioulasso, secteur 21, face station",
          description:
            "Diagnostic, vidange, pneus et depannage moto avec contact WhatsApp direct.",
          latitude: 11.1784,
          longitude: -4.2979,
          status: "published",
          photos: [],
          rating_average: 4.3,
          rating_count: 8,
          comments: []
        },
        {
          id: "biz_elec",
          owner_id: "user_demo",
          name: "Electricite Faso Service",
          category: "Electricien",
          phone: "+22670000003",
          opening_hours: "Lun-Dim, urgence 24h/24",
          address_description: "Ouagadougou, Patte d'Oie, non loin du rond-point",
          description:
            "Installation domestique, depannage, tableau electrique et entretien.",
          latitude: 12.3261,
          longitude: -1.5228,
          status: "draft",
          photos: [],
          rating_average: 0,
          rating_count: 0,
          comments: []
        }
      ]
    };
  }

  function getStore() {
    const existing = localStorage.getItem(storeKey);
    if (!existing) {
      const seeded = defaultStore();
      localStorage.setItem(storeKey, JSON.stringify(seeded));
      return seeded;
    }

    try {
      return JSON.parse(existing);
    } catch (error) {
      const seeded = defaultStore();
      localStorage.setItem(storeKey, JSON.stringify(seeded));
      return seeded;
    }
  }

  function saveStore(store) {
    localStorage.setItem(storeKey, JSON.stringify(store));
  }

  function getToken() {
    return localStorage.getItem(window.AppConfig.tokenKey);
  }

  function setSession(token, user) {
    localStorage.setItem(window.AppConfig.tokenKey, token);
    localStorage.setItem(window.AppConfig.userKey, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem(window.AppConfig.tokenKey);
    localStorage.removeItem(window.AppConfig.userKey);
  }

  function currentLocalUser() {
    const userJson = localStorage.getItem(window.AppConfig.userKey);
    if (!userJson) return null;
    try {
      return JSON.parse(userJson);
    } catch (error) {
      return null;
    }
  }

  function authIdentifier(payload) {
    return String(payload.identifier || payload.phone || payload.email || "").trim();
  }

  function backendLoginPayload(payload) {
    return {
      identifier: authIdentifier(payload),
      password: payload.password
    };
  }

  function backendIdentifierPayload(payload) {
    return {
      ...payload,
      identifier: authIdentifier(payload)
    };
  }

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = getToken();

    if (!(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${window.AppConfig.apiBaseUrl}${path}`, {
      ...options,
      headers
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const message =
        typeof payload === "string"
          ? payload
          : payload.detail || payload.message || "Erreur API";
      throw new Error(message);
    }

    return payload;
  }

  function normalizePhoto(photo) {
    const rawPath =
      typeof photo === "string"
        ? photo
        : photo && (photo.file_path || photo.photo_url || photo.url);
    if (!rawPath) return "";
    if (/^(https?:|data:|blob:)/.test(rawPath)) return rawPath;
    if (rawPath.startsWith("/")) return `${window.AppConfig.apiBaseUrl}${rawPath}`;
    return rawPath;
  }

  function normalizeComment(comment) {
    if (!comment) return null;
    return {
      id: comment.id,
      business_id: comment.business_id,
      author_name: comment.author_name || "Client",
      content: comment.content || comment.comment || "",
      rating: comment.rating ?? comment.ai_rating,
      justification: comment.justification || comment.ai_explanation || "",
      created_at: comment.created_at
    };
  }

  function googleMapsPlaceUrl(business) {
    const lat = Number(business.latitude);
    const lng = Number(business.longitude);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return "";
    const query = `${business.name || ""} ${lat},${lng}`.trim();
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
  }

  function googleMapsNavigationUrl(business, origin) {
    const lat = Number(business.latitude);
    const lng = Number(business.longitude);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return "";
    const params = new URLSearchParams({
      api: "1",
      destination: `${lat},${lng}`,
      travelmode: "walking"
    });
    if (origin) params.set("origin", `${origin.latitude},${origin.longitude}`);
    return `https://www.google.com/maps/dir/?${params.toString()}`;
  }

  function openStreetMapUrl(business) {
    const lat = Number(business.latitude);
    const lng = Number(business.longitude);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return "";
    return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=18/${lat}/${lng}`;
  }

  function cleanBusinessPayload(business) {
    const ratingAverage = Number(business.rating_average ?? business.average_rating ?? 0);
    const ratingCount = Number(
      business.rating_count ?? business.ratings_count ?? business.reviews_count ?? 0
    );
    const normalized = {
      id: business.id,
      name: business.name,
      category: business.category,
      phone: business.phone,
      opening_hours: business.opening_hours,
      address_description: business.address_description,
      description: business.description,
      latitude: Number(business.latitude),
      longitude: Number(business.longitude),
      status: business.status,
      photos: (business.photos || []).map(normalizePhoto).filter(Boolean),
      rating_average: ratingAverage,
      rating_count: ratingCount,
      distance_km: business.distance_km,
      google_maps_url: business.google_maps_url,
      google_navigation_url: business.google_navigation_url,
      openstreetmap_url: business.openstreetmap_url,
      comments: (business.comments || []).map(normalizeComment).filter(Boolean)
    };
    normalized.google_maps_url = normalized.google_maps_url || googleMapsPlaceUrl(normalized);
    normalized.google_navigation_url =
      normalized.google_navigation_url || googleMapsNavigationUrl(normalized);
    normalized.openstreetmap_url = normalized.openstreetmap_url || openStreetMapUrl(normalized);
    return normalized;
  }

  const DemoApi = {
    async register(payload) {
      const store = getStore();
      const phone = String(payload.phone || "").trim();
      if (!phone || !payload.password || !payload.full_name) {
        throw new Error("Nom, telephone et mot de passe sont requis.");
      }
      if (store.users.some((user) => user.phone === phone)) {
        throw new Error("Ce telephone existe deja.");
      }
      const user = {
        id: uid("user"),
        full_name: payload.full_name,
        phone,
        password: payload.password
      };
      store.users.push(user);
      saveStore(store);
      const publicUser = { id: user.id, full_name: user.full_name, phone };
      setSession(`demo.${user.id}`, publicUser);
      return { access_token: `demo.${user.id}`, user: publicUser };
    },

    async login(payload) {
      const store = getStore();
      const phone = String(payload.phone || "").trim();
      const user = store.users.find(
        (item) => item.phone === phone && item.password === payload.password
      );
      if (!user) {
        throw new Error("Telephone ou mot de passe incorrect. Essai rapide: +22670000000 / demo1234.");
      }
      const publicUser = {
        id: user.id,
        full_name: user.full_name,
        phone: user.phone
      };
      setSession(`demo.${user.id}`, publicUser);
      return { access_token: `demo.${user.id}`, user: publicUser };
    },

    async me() {
      const user = currentLocalUser();
      if (!user) throw new Error("Session absente.");
      return user;
    },

    async forgotPassword(payload) {
      const store = getStore();
      const phone = String(payload.phone || "").trim();
      if (!store.users.some((user) => user.phone === phone)) {
        throw new Error("Aucun compte trouve avec ce telephone.");
      }
      store.resetCodes[phone] = "202600";
      saveStore(store);
      return { reset_code: "202600", message: "Code de test pret." };
    },

    async resetPassword(payload) {
      const store = getStore();
      const phone = String(payload.phone || "").trim();
      if (store.resetCodes[phone] !== String(payload.code || "")) {
        throw new Error("Code reset incorrect.");
      }
      const user = store.users.find((item) => item.phone === phone);
      user.password = payload.new_password;
      delete store.resetCodes[phone];
      saveStore(store);
      return { message: "Mot de passe modifie." };
    },

    async createBusiness(payload) {
      const store = getStore();
      const user = currentLocalUser();
      if (!user) throw new Error("Connexion requise.");
      const business = {
        ...payload,
        id: uid("biz"),
        owner_id: user.id,
        status: "draft",
        photos: [],
        rating_average: 0,
        rating_count: 0,
        comments: []
      };
      store.businesses.unshift(business);
      saveStore(store);
      return cleanBusinessPayload(business);
    },

    async myBusinesses() {
      const store = getStore();
      const user = currentLocalUser();
      if (!user) throw new Error("Connexion requise.");
      return store.businesses
        .filter((business) => business.owner_id === user.id)
        .map(cleanBusinessPayload);
    },

    async publishBusiness(id) {
      const store = getStore();
      const business = store.businesses.find((item) => item.id === id);
      if (!business) throw new Error("Commerce introuvable.");
      business.status = "published";
      saveStore(store);
      return cleanBusinessPayload(business);
    },

    async unpublishBusiness(id) {
      const store = getStore();
      const business = store.businesses.find((item) => item.id === id);
      if (!business) throw new Error("Commerce introuvable.");
      business.status = "draft";
      saveStore(store);
      return cleanBusinessPayload(business);
    },

    async uploadPhotos(id, files) {
      const store = getStore();
      const business = store.businesses.find((item) => item.id === id);
      if (!business) throw new Error("Commerce introuvable.");

      const selectedFiles = Array.from(files || []).slice(0, 3);
      const encoded = await Promise.all(
        selectedFiles.map(
          (file) =>
            new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result);
              reader.onerror = reject;
              reader.readAsDataURL(file);
            })
        )
      );
      business.photos = encoded;
      saveStore(store);
      return { photos: business.photos };
    },

    async searchBusinesses(params = {}) {
      const store = getStore();
      const query = normalizeText(params.q || params.name || "");
      const category = normalizeText(params.category || "");
      const minRating = Number(params.min_rating || 0);
      const lat = params.lat ? Number(params.lat) : null;
      const lng = params.lng ? Number(params.lng) : null;

      return store.businesses
        .filter((business) => business.status === "published")
        .map((business) => {
          const distance =
            lat !== null && lng !== null
              ? distanceKm(lat, lng, business.latitude, business.longitude)
              : null;
          return { ...cleanBusinessPayload(business), distance_km: distance };
        })
        .filter((business) => {
          const haystack = normalizeText(
            `${business.name} ${business.category} ${business.address_description}`
          );
          const queryOk = !query || haystack.includes(query);
          const categoryOk = !category || normalizeText(business.category) === category;
          const ratingOk = Number(business.rating_average || 0) >= minRating;
          return queryOk && categoryOk && ratingOk;
        })
        .sort((a, b) => {
          if (a.distance_km !== null && b.distance_km !== null) {
            return a.distance_km - b.distance_km;
          }
          return Number(b.rating_average || 0) - Number(a.rating_average || 0);
        });
    },

    async findBusiness(id) {
      const store = getStore();
      const business = store.businesses.find((item) => String(item.id) === String(id));
      return business ? cleanBusinessPayload(business) : null;
    },

    async listComments(id) {
      const business = await this.findBusiness(id);
      return business ? business.comments : [];
    },

    async addComment(id, payload) {
      const store = getStore();
      const business = store.businesses.find((item) => String(item.id) === String(id));
      if (!business) throw new Error("Commerce introuvable.");
      const rating = keywordRating(payload.content);
      const comment = {
        id: uid("com"),
        author_name: payload.author_name || "Client",
        content: payload.content,
        rating: rating.rating,
        justification: rating.justification,
        created_at: new Date().toISOString().slice(0, 10)
      };
      business.comments = business.comments || [];
      business.comments.unshift(comment);
      business.rating_count = business.comments.length;
      business.rating_average =
        business.comments.reduce((sum, item) => sum + Number(item.rating), 0) /
        business.rating_count;
      saveStore(store);
      return { comment, business: cleanBusinessPayload(business) };
    },

    async rateComment(payload) {
      return keywordRating(payload.content || payload.comment || "");
    }
  };

  async function withFallback(realRequest, fallbackRequest) {
    try {
      return await realRequest();
    } catch (error) {
      if (!window.AppConfig.demoModeEnabled) throw error;
      console.warn("Backend indisponible, donnees de test utilisees.", error);
      if (window.UI && window.UI.toast) {
        window.UI.toast("Backend non joignable: on continue avec les donnees de test.", "warning");
      }
      return fallbackRequest();
    }
  }

  window.Api = {
    getToken,
    clearSession,
    currentUser: currentLocalUser,

    async register(payload) {
      return withFallback(
        async () => {
          await request("/auth/register", {
            method: "POST",
            body: JSON.stringify(payload)
          });
          const data = await request("/auth/login", {
            method: "POST",
            body: JSON.stringify(backendLoginPayload(payload))
          });
          setSession(data.access_token, data.user);
          return data;
        },
        () => DemoApi.register(payload)
      );
    },

    async login(payload) {
      return withFallback(
        async () => {
          const data = await request("/auth/login", {
            method: "POST",
            body: JSON.stringify(backendLoginPayload(payload))
          });
          setSession(data.access_token, data.user);
          return data;
        },
        () => DemoApi.login(payload)
      );
    },

    async me() {
      return withFallback(() => request("/auth/me"), () => DemoApi.me());
    },

    async forgotPassword(payload) {
      return withFallback(
        async () => {
          const data = await request("/auth/forgot-password", {
            method: "POST",
            body: JSON.stringify(backendIdentifierPayload(payload))
          });
          return {
            ...data,
            reset_code: data.demo_reset_code || data.reset_code
          };
        },
        () => DemoApi.forgotPassword(payload)
      );
    },

    async resetPassword(payload) {
      return withFallback(
        () =>
          request("/auth/reset-password", {
            method: "POST",
            body: JSON.stringify(backendIdentifierPayload(payload))
          }),
        () => DemoApi.resetPassword(payload)
      );
    },

    async createBusiness(payload) {
      return withFallback(
        async () => {
          const data = await request("/businesses", {
            method: "POST",
            body: JSON.stringify(payload)
          });
          return cleanBusinessPayload(data);
        },
        () => DemoApi.createBusiness(payload)
      );
    },

    async myBusinesses() {
      return withFallback(
        async () => {
          const data = await request("/my-businesses");
          return data.map(cleanBusinessPayload);
        },
        () => DemoApi.myBusinesses()
      );
    },

    async publishBusiness(id) {
      return withFallback(
        async () => {
          const data = await request(`/businesses/${encodeURIComponent(id)}/publish`, { method: "PATCH" });
          return cleanBusinessPayload(data);
        },
        () => DemoApi.publishBusiness(id)
      );
    },

    async unpublishBusiness(id) {
      return withFallback(
        async () => {
          const data = await request(`/businesses/${encodeURIComponent(id)}/unpublish`, {
            method: "PATCH"
          });
          return cleanBusinessPayload(data);
        },
        () => DemoApi.unpublishBusiness(id)
      );
    },

    async uploadPhotos(id, files) {
      return withFallback(
        async () => {
          const uploaded = [];
          for (const file of Array.from(files || []).slice(0, 3)) {
            const formData = new FormData();
            formData.append("file", file);
            uploaded.push(
              await request(`/businesses/${encodeURIComponent(id)}/photos`, {
                method: "POST",
                body: formData
              })
            );
          }
          return { photos: uploaded.map(normalizePhoto).filter(Boolean) };
        },
        () => DemoApi.uploadPhotos(id, files)
      );
    },

    async searchBusinesses(params = {}) {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          query.set(key, value);
        }
      });
      const suffix = query.toString() ? `?${query.toString()}` : "";
      return withFallback(
        async () => {
          const data = await request(`/search${suffix}`);
          return data.map(cleanBusinessPayload);
        },
        () => DemoApi.searchBusinesses(params)
      );
    },

    async businessDetail(id) {
      return withFallback(
        async () => {
          const data = await request(`/businesses/${encodeURIComponent(id)}`);
          const business = cleanBusinessPayload(data);
          try {
            const comments = await request(`/businesses/${encodeURIComponent(id)}/comments`);
            business.comments = comments.map(normalizeComment).filter(Boolean);
          } catch (error) {
            business.comments = [];
          }
          return business;
        },
        () => DemoApi.findBusiness(id)
      );
    },

    async listComments(id) {
      return withFallback(
        async () => {
          const data = await request(`/businesses/${encodeURIComponent(id)}/comments`);
          return data.map(normalizeComment).filter(Boolean);
        },
        () => DemoApi.listComments(id)
      );
    },

    async findBusiness(id) {
      const business = await this.businessDetail(id);
      if (business) return business;
      const businesses = await this.searchBusinesses({});
      return businesses.find((item) => String(item.id) === String(id));
    },

    async addComment(id, payload) {
      return withFallback(
        async () => {
          const data = await request(`/businesses/${encodeURIComponent(id)}/comments`, {
            method: "POST",
            body: JSON.stringify({
              comment: payload.comment || payload.content,
              user_id: payload.user_id
            })
          });
          return { comment: normalizeComment({ ...data, author_name: payload.author_name }) };
        },
        () => DemoApi.addComment(id, payload)
      );
    },

    async rateComment(payload) {
      return withFallback(
        () =>
          request("/ai/rate-comment", {
            method: "POST",
            body: JSON.stringify({ comment: payload.comment || payload.content })
          }),
        () => DemoApi.rateComment(payload)
      );
    },

    googleMapsNavigationUrl,
    googleMapsPlaceUrl
  };
})();
