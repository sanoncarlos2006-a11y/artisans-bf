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

  function cleanBusinessPayload(business) {
    return {
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
      photos: business.photos || [],
      rating_average: Number(business.rating_average || 0),
      rating_count: Number(business.rating_count || 0),
      comments: business.comments || []
    };
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
      store.resetCodes[phone] = "2026";
      saveStore(store);
      return { reset_code: "2026", message: "Code de test pret." };
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

    async addComment(id, payload) {
      const store = getStore();
      const business = store.businesses.find((item) => item.id === id);
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
          const data = await request("/auth/register", {
            method: "POST",
            body: JSON.stringify(payload)
          });
          const token = data.access_token || data.token;
          if (token) setSession(token, data.user || data);
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
            body: JSON.stringify(payload)
          });
          const token = data.access_token || data.token;
          if (token) setSession(token, data.user || { phone: payload.phone });
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
        () =>
          request("/auth/forgot-password", {
            method: "POST",
            body: JSON.stringify(payload)
          }),
        () => DemoApi.forgotPassword(payload)
      );
    },

    async resetPassword(payload) {
      return withFallback(
        () =>
          request("/auth/reset-password", {
            method: "POST",
            body: JSON.stringify(payload)
          }),
        () => DemoApi.resetPassword(payload)
      );
    },

    async createBusiness(payload) {
      return withFallback(
        () =>
          request("/businesses", {
            method: "POST",
            body: JSON.stringify(payload)
          }),
        () => DemoApi.createBusiness(payload)
      );
    },

    async myBusinesses() {
      return withFallback(() => request("/my-businesses"), () => DemoApi.myBusinesses());
    },

    async publishBusiness(id) {
      return withFallback(
        () => request(`/businesses/${encodeURIComponent(id)}/publish`, { method: "PATCH" }),
        () => DemoApi.publishBusiness(id)
      );
    },

    async unpublishBusiness(id) {
      return withFallback(
        () =>
          request(`/businesses/${encodeURIComponent(id)}/unpublish`, {
            method: "PATCH"
          }),
        () => DemoApi.unpublishBusiness(id)
      );
    },

    async uploadPhotos(id, files) {
      return withFallback(
        () => {
          const formData = new FormData();
          Array.from(files || [])
            .slice(0, 3)
            .forEach((file) => formData.append("photos", file));
          return request(`/businesses/${encodeURIComponent(id)}/photos`, {
            method: "POST",
            body: formData
          });
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
        () => request(`/search${suffix}`),
        () => DemoApi.searchBusinesses(params)
      );
    },

    async findBusiness(id) {
      const businesses = await this.searchBusinesses({});
      return businesses.find((business) => String(business.id) === String(id));
    },

    async addComment(id, payload) {
      return withFallback(
        () =>
          request(`/businesses/${encodeURIComponent(id)}/comments`, {
            method: "POST",
            body: JSON.stringify(payload)
          }),
        () => DemoApi.addComment(id, payload)
      );
    },

    async rateComment(payload) {
      return withFallback(
        () =>
          request("/ai/rate-comment", {
            method: "POST",
            body: JSON.stringify(payload)
          }),
        () => DemoApi.rateComment(payload)
      );
    }
  };
})();
