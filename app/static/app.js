const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatThread = document.getElementById("chat-thread");
const destinationGrid = document.getElementById("destination-grid");
const resultsPanel = document.getElementById("results-panel");
const debugPills = document.getElementById("debug-pills");
const statusPill = document.getElementById("status-pill");
const sendButton = document.getElementById("send-button");
const promptChips = document.querySelectorAll(".prompt-chip");
const modeSelect = document.getElementById("mode-select");
const languageSelect = document.getElementById("language-select");
const assistantToggle = document.getElementById("assistant-toggle");
const technicalPanel = document.getElementById("technical-panel");
const requestJson = document.getElementById("request-json");
const responseJson = document.getElementById("response-json");
const pageShell = document.querySelector(".page-shell");

const conversationHistory = [];
let currentLanguage = "en";
let currentMode = "demo";
let assistantVisible = true;

const translations = {
  en: {
    heroEyebrow: "Travel Recommendation PoC",
    heroTitle: "Find the right destination through conversation, not filter menus.",
    heroText: "This demo uses an LLM to interpret travel intent and GraphQL to retrieve structured destination matches.",
    howItWorksLabel: "How it works",
    howItWorks1: "Understand traveler intent",
    howItWorks2: "Translate it into filters",
    howItWorks3: "Query structured destination data",
    howItWorks4: "Explain the best matches clearly",
    promptLabel: "Try one of these",
    prompt1: "Cheap sunny trip in summer",
    prompt2: "Family beach holiday in Spain",
    prompt3: "Romantic city trip in autumn",
    chatEyebrow: "Hybrid Agent",
    chatTitle: "Destination chat",
    languageLabel: "Language",
    modeLabel: "Mode",
    hideAssistant: "Hide assistant",
    showAssistant: "Show assistant",
    assistantLabel: "Assistant",
    travelerLabel: "Traveler",
    openingMessage: "Tell me what kind of trip you want and I’ll turn that into destination filters, search the dataset, and recommend a few matching places.",
    resultsEyebrow: "Retrieved matches",
    resultsTitle: "Recommended destinations",
    technicalEyebrow: "Technical trace",
    technicalTitle: "API calls and responses",
    requestTitle: "Request payload",
    responseTitle: "Response payload",
    composerLabel: "Ask for a destination",
    composerPlaceholder: "Example: I want a warm beach destination under 180 euro in autumn",
    composerHint: "The chat keeps lightweight conversation history and uses the structured GraphQL retrieval layer underneath.",
    search: "Search",
    searching: "Searching...",
    ready: "Ready",
    thinking: "Thinking",
    error: "Error",
    requestFailed: "Something went wrong while contacting the agent. Please check the API server and try again.",
    noDestinationTitle: "No destination matches yet",
    noDestinationBody: "Try broadening your budget, season, or travel style.",
    fromEur: "From EUR",
    priceCategory: "Price category",
    tripTags: "Trip tags",
    bestSeasons: "Best seasons",
    technical: "Technical",
    demo: "Demo",
    termLabel: "term",
  },
  nl: {
    heroEyebrow: "Travel Recommendation PoC",
    heroTitle: "Vind de juiste bestemming via een gesprek, niet via filtermenu's.",
    heroText: "Deze demo gebruikt een LLM om reisintentie te interpreteren en GraphQL om gestructureerde bestemmingen op te halen.",
    howItWorksLabel: "Hoe het werkt",
    howItWorks1: "Begrijp de reisintentie van de gebruiker",
    howItWorks2: "Vertaal dit naar filters",
    howItWorks3: "Doorzoek de gestructureerde bestemmingsdata",
    howItWorks4: "Leg de beste matches helder uit",
    promptLabel: "Probeer bijvoorbeeld",
    prompt1: "Goedkope zonnige trip in de zomer",
    prompt2: "Familievriendelijke strandvakantie in Spanje",
    prompt3: "Romantische stedentrip in de herfst",
    chatEyebrow: "Hybride Agent",
    chatTitle: "Bestemmingschat",
    languageLabel: "Taal",
    modeLabel: "Modus",
    hideAssistant: "Verberg assistent",
    showAssistant: "Toon assistent",
    assistantLabel: "Assistent",
    travelerLabel: "Reiziger",
    openingMessage: "Vertel welk type reis je zoekt en ik zet dat om naar filters, doorzoek de dataset en geef een paar passende bestemmingen terug.",
    resultsEyebrow: "Opgehaalde matches",
    resultsTitle: "Aanbevolen bestemmingen",
    technicalEyebrow: "Technische trace",
    technicalTitle: "API-calls en responses",
    requestTitle: "Request payload",
    responseTitle: "Response payload",
    composerLabel: "Vraag om een bestemming",
    composerPlaceholder: "Voorbeeld: Ik wil een warme strandbestemming onder 180 euro in de herfst",
    composerHint: "De chat bewaart lichte conversatiegeschiedenis en gebruikt daaronder de gestructureerde GraphQL retrieval-laag.",
    search: "Zoek",
    searching: "Zoeken...",
    ready: "Klaar",
    thinking: "Denkt na",
    error: "Fout",
    requestFailed: "Er ging iets mis bij het benaderen van de agent. Controleer de API-server en probeer opnieuw.",
    noDestinationTitle: "Nog geen passende bestemmingen",
    noDestinationBody: "Probeer je budget, seizoen of reisstijl iets ruimer te maken.",
    fromEur: "Vanaf EUR",
    priceCategory: "Prijscategorie",
    tripTags: "Trip tags",
    bestSeasons: "Beste seizoenen",
    technical: "Technisch",
    demo: "Demo",
    termLabel: "term",
  },
  fr: {
    heroEyebrow: "PoC de recommandation voyage",
    heroTitle: "Trouvez la bonne destination par la conversation, pas par des menus de filtres.",
    heroText: "Cette demo utilise un LLM pour interpreter l'intention voyage et GraphQL pour recuperer des destinations structurees.",
    howItWorksLabel: "Comment ca marche",
    howItWorks1: "Comprendre l'intention du voyageur",
    howItWorks2: "La traduire en filtres",
    howItWorks3: "Interroger des donnees structurees",
    howItWorks4: "Expliquer clairement les meilleurs choix",
    promptLabel: "Essayez par exemple",
    prompt1: "Voyage ensoleille et abordable en ete",
    prompt2: "Vacances a la plage en Espagne pour toute la famille",
    prompt3: "City trip romantique en automne",
    chatEyebrow: "Agent hybride",
    chatTitle: "Chat destination",
    languageLabel: "Langue",
    modeLabel: "Mode",
    hideAssistant: "Masquer l'assistant",
    showAssistant: "Afficher l'assistant",
    assistantLabel: "Assistant",
    travelerLabel: "Voyageur",
    openingMessage: "Dites-moi quel type de voyage vous cherchez et je le traduirai en filtres, j'interrogerai le dataset et je recommanderai quelques destinations adaptees.",
    resultsEyebrow: "Correspondances recuperees",
    resultsTitle: "Destinations recommandees",
    technicalEyebrow: "Trace technique",
    technicalTitle: "Appels API et reponses",
    requestTitle: "Payload de requete",
    responseTitle: "Payload de reponse",
    composerLabel: "Demander une destination",
    composerPlaceholder: "Exemple : Je veux une destination plage et chaude a moins de 180 euros en automne",
    composerHint: "Le chat conserve un historique leger et s'appuie sur la couche GraphQL de retrieval structuree.",
    search: "Chercher",
    searching: "Recherche...",
    ready: "Pret",
    thinking: "Analyse",
    error: "Erreur",
    requestFailed: "Une erreur s'est produite lors du contact avec l'agent. Verifiez l'API et reessayez.",
    noDestinationTitle: "Aucune destination correspondante pour l'instant",
    noDestinationBody: "Essayez d'elargir votre budget, la saison ou le style de voyage.",
    fromEur: "A partir de EUR",
    priceCategory: "Categorie de prix",
    tripTags: "Tags de voyage",
    bestSeasons: "Meilleures saisons",
    technical: "Technique",
    demo: "Demo",
    termLabel: "terme",
  },
};

applyTranslations();
applyMode();
updateAssistantToggleLabel();
updateAssistantThreadVisibility();

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  messageInput.value = "";
  setBusyState(true);

  const requestPayload = {
    message,
    limit: 5,
    chat_history: conversationHistory,
    response_language: currentLanguage,
  };
  renderTechnicalTrace(requestPayload, null);

  try {
    const response = await fetch("/agent/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const payload = await response.json();
    appendMessage("assistant", payload.answer);
    renderResults(payload);
    renderTechnicalTrace(requestPayload, payload);
    conversationHistory.push({ role: "user", content: message });
    conversationHistory.push({ role: "assistant", content: payload.answer });
    statusPill.textContent = t("ready");
  } catch (error) {
    appendMessage("assistant", t("requestFailed"));
    statusPill.textContent = t("error");
    console.error(error);
  } finally {
    setBusyState(false);
  }
});

promptChips.forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset[`prompt${currentLanguage.toUpperCase()}`] || button.dataset.promptEn || "";
    messageInput.focus();
  });
});

modeSelect.addEventListener("change", () => {
  currentMode = modeSelect.value;
  applyMode();
});

languageSelect.addEventListener("change", () => {
  currentLanguage = languageSelect.value;
  applyTranslations();
  updateAssistantToggleLabel();
  if (!sendButton.disabled) {
    sendButton.textContent = t("search");
  }
});

assistantToggle.addEventListener("click", () => {
  assistantVisible = !assistantVisible;
  pageShell.classList.toggle("assistant-hidden", !assistantVisible);
  updateAssistantToggleLabel();
  updateAssistantThreadVisibility();
});

function appendMessage(role, content) {
  const message = document.createElement("article");
  message.className = `message ${role}`;

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? t("travelerLabel") : t("assistantLabel");

  const body = document.createElement("p");
  body.textContent = content;

  message.append(meta, body);
  if (role === "assistant" && !assistantVisible) {
    message.hidden = true;
  }
  chatThread.appendChild(message);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function renderResults(payload) {
  destinationGrid.innerHTML = "";
  debugPills.innerHTML = "";

  const filters = payload.applied_filters || {};
  const debugEntries = [
    ...Object.entries(filters)
      .filter(([, value]) => value !== null && value !== "")
      .map(([key, value]) => `${humanizeKey(key)}: ${value}`),
    ...(payload.matched_terms || []).map((term) => `${t("termLabel")}: ${term}`),
  ];

  debugEntries.forEach((text) => {
    const pill = document.createElement("span");
    pill.className = "debug-pill";
    pill.textContent = text;
    debugPills.appendChild(pill);
  });

  const destinations = payload.destinations || [];
  if (!destinations.length) {
    resultsPanel.hidden = false;
    const emptyCard = document.createElement("article");
    emptyCard.className = "destination-card";
    emptyCard.innerHTML = `
      <h4>${t("noDestinationTitle")}</h4>
      <p class="destination-subtitle">${t("noDestinationBody")}</p>
    `;
    destinationGrid.appendChild(emptyCard);
    return;
  }

  destinations.forEach((destination) => {
    const card = document.createElement("article");
    card.className = "destination-card";
    card.innerHTML = `
      <h4>${destination.destination_name}</h4>
      <p class="destination-subtitle">${destination.destination_country}</p>
      <div class="destination-price">${t("fromEur")} ${Math.round(destination.estimated_from_price_eur)}</div>
      <p class="destination-meta">${t("priceCategory")}: ${destination.price_category}</p>
      <p class="destination-tags">${t("tripTags")}: ${destination.trip_tags}</p>
      <p class="destination-tags">${t("bestSeasons")}: ${destination.best_seasons}</p>
    `;
    destinationGrid.appendChild(card);
  });

  resultsPanel.hidden = false;
}

function renderTechnicalTrace(requestPayload, responsePayload) {
  requestJson.textContent = prettyJson(requestPayload);
  responseJson.textContent = responsePayload ? prettyJson(responsePayload) : "";
}

function setBusyState(isBusy) {
  sendButton.disabled = isBusy;
  sendButton.textContent = isBusy ? t("searching") : t("search");
  statusPill.textContent = isBusy ? t("thinking") : t("ready");
}

function humanizeKey(key) {
  return key.replaceAll("_", " ");
}

function applyTranslations() {
  document.documentElement.lang = currentLanguage;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (translations[currentLanguage][key]) {
      element.textContent = translations[currentLanguage][key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    const key = element.dataset.i18nPlaceholder;
    if (translations[currentLanguage][key]) {
      element.setAttribute("placeholder", translations[currentLanguage][key]);
    }
  });

  Array.from(modeSelect.options).forEach((option) => {
    option.textContent = t(option.value);
  });
}

function applyMode() {
  const showTechnical = currentMode === "technical";
  technicalPanel.hidden = !showTechnical;
  debugPills.style.display = showTechnical ? "flex" : "none";
}

function updateAssistantToggleLabel() {
  assistantToggle.textContent = assistantVisible ? t("hideAssistant") : t("showAssistant");
}

function updateAssistantThreadVisibility() {
  document.querySelectorAll(".message.assistant").forEach((message) => {
    message.hidden = !assistantVisible;
  });
}

function prettyJson(value) {
  return JSON.stringify(value, null, 2);
}

function t(key) {
  return translations[currentLanguage][key] || translations.en[key] || key;
}
