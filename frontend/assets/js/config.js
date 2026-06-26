(function () {
  const categories = [
    "Mecanicien",
    "Couturier",
    "Coiffeur",
    "Soudeur",
    "Menuisier",
    "Plombier",
    "Electricien",
    "Reparateur telephone",
    "Restaurant",
    "Boutique",
    "Autre"
  ];

  window.AppConfig = {
    apiBaseUrl:
      localStorage.getItem("annuaire_api_base_url") || "http://127.0.0.1:8000",
    demoModeEnabled: true,
    tokenKey: "annuaire_auth_token",
    userKey: "annuaire_current_user",
    categories
  };
})();
