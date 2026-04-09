const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatThread = document.getElementById("chat-thread");
const destinationGrid = document.getElementById("destination-grid");
const resultsPanel = document.getElementById("results-panel");
const debugPills = document.getElementById("debug-pills");
const statusPill = document.getElementById("status-pill");
const sendButton = document.getElementById("send-button");
const sendButtonLabel = document.getElementById("send-button-label");
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
let showPromptPlaceholder = true;

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
    summaryTitle: "Trip summary",
    architectureEyebrow: "Structured LLM data call",
    architectureTitle: "Runtime flow from user to dataset and back",
    archStep1: "1",
    archStep2: "2",
    archStep3: "3",
    archStep4: "4",
    archStep5: "5",
    archStep6: "6",
    archStep7: "7",
    archStep8: "8",
    archStep9: "9",
    archStep10: "10",
    archStep11: "11",
    archUserTitle: "User",
    archUserBody: "Asks for a destination in natural language.",
    archChatTitle: "Chat UI",
    archChatBody: "Collects the prompt, language, and chat context.",
    archLlmIntentTitle: "LLM (pre-search)",
    archLlmIntentBody: "Interprets intent and maps it to structured filters.",
    archMcpTitle: "MCP",
    archMcpBody: "Future integration point between the LLM/tool layer and structured retrieval. Not active here because this PoC keeps the stack simple.",
    archStructuredTitle: "Structured retrieval call",
    archStructuredBody: "FastAPI agent service makes a controlled GraphQL data call.",
    archGraphqlTitle: "GraphQL",
    archGraphqlBody: "Executes the destination query with explicit arguments.",
    archOrmTitle: "SQLAlchemy",
    archOrmBody: "Builds deterministic ORM filters against the destination model.",
    archDbTitle: "SQLite",
    archDbBody: "Reads the local structured travel dataset quickly.",
    archDatasetTitle: "Destination dataset",
    archDatasetBody: "CSV-origin structured destination records remain the source of truth.",
    archLlmPostTitle: "LLM (post-search)",
    archLlmPostBody: "Writes compact recommendation text for the result cards.",
    archReturnTitle: "User",
    archReturnBody: "Receives the interpreted request plus destination recommendations back in the chat UI.",
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
    summaryTitle: "Reissamenvatting",
    architectureEyebrow: "Structured LLM data call",
    architectureTitle: "Runtime flow van gebruiker naar dataset en terug",
    archStep1: "1",
    archStep2: "2",
    archStep3: "3",
    archStep4: "4",
    archStep5: "5",
    archStep6: "6",
    archStep7: "7",
    archStep8: "8",
    archStep9: "9",
    archStep10: "10",
    archStep11: "11",
    archUserTitle: "Gebruiker",
    archUserBody: "Stelt een bestemmingsvraag in natuurlijke taal.",
    archChatTitle: "Chat UI",
    archChatBody: "Verzamelt de prompt, taal en chatcontext.",
    archLlmIntentTitle: "LLM (pre-search)",
    archLlmIntentBody: "Interpreteert intentie en zet die om naar gestructureerde filters.",
    archMcpTitle: "MCP",
    archMcpBody: "Toekomstig integratiepunt tussen de LLM/tool-laag en structured retrieval. Niet actief in deze PoC omdat de stack bewust simpel blijft.",
    archStructuredTitle: "Structured retrieval call",
    archStructuredBody: "De FastAPI agent service doet een gecontroleerde GraphQL-datacall.",
    archGraphqlTitle: "GraphQL",
    archGraphqlBody: "Voert de bestemmingsquery uit met expliciete argumenten.",
    archOrmTitle: "SQLAlchemy",
    archOrmBody: "Bouwt deterministische ORM-filters tegen het destination model.",
    archDbTitle: "SQLite",
    archDbBody: "Leest de lokale gestructureerde travel dataset snel uit.",
    archDatasetTitle: "Destination dataset",
    archDatasetBody: "CSV-gebaseerde destination records blijven de source of truth.",
    archLlmPostTitle: "LLM (post-search)",
    archLlmPostBody: "Schrijft compacte recommendation-tekst voor de result cards.",
    archReturnTitle: "Gebruiker",
    archReturnBody: "Krijgt de geinterpreteerde vraag en de bestemmingsaanbevelingen terug in de chat UI.",
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
    summaryTitle: "Resume du voyage",
    architectureEyebrow: "Structured LLM data call",
    architectureTitle: "Flux runtime de l utilisateur vers le dataset puis retour",
    archStep1: "1",
    archStep2: "2",
    archStep3: "3",
    archStep4: "4",
    archStep5: "5",
    archStep6: "6",
    archStep7: "7",
    archStep8: "8",
    archStep9: "9",
    archStep10: "10",
    archStep11: "11",
    archUserTitle: "Utilisateur",
    archUserBody: "Formule une demande de destination en langage naturel.",
    archChatTitle: "Chat UI",
    archChatBody: "Recueille le prompt, la langue et le contexte du chat.",
    archLlmIntentTitle: "LLM (pre-search)",
    archLlmIntentBody: "Interprete l intention et la convertit en filtres structures.",
    archMcpTitle: "MCP",
    archMcpBody: "Point d integration futur entre la couche LLM/outils et le retrieval structure. Pas actif ici car cette PoC garde une stack simple.",
    archStructuredTitle: "Structured retrieval call",
    archStructuredBody: "Le service agent FastAPI effectue un appel de donnees GraphQL controle.",
    archGraphqlTitle: "GraphQL",
    archGraphqlBody: "Execute la requete destination avec des arguments explicites.",
    archOrmTitle: "SQLAlchemy",
    archOrmBody: "Construit des filtres ORM deterministes sur le modele destination.",
    archDbTitle: "SQLite",
    archDbBody: "Lit rapidement le dataset voyage structure local.",
    archDatasetTitle: "Dataset destinations",
    archDatasetBody: "Les enregistrements destination issus du CSV restent la source de verite.",
    archLlmPostTitle: "LLM (post-search)",
    archLlmPostBody: "Redige un texte de recommandation compact pour les cartes resultat.",
    archReturnTitle: "Utilisateur",
    archReturnBody: "Recoit l interpretation de la requete et les recommandations dans la chat UI.",
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
  showPromptPlaceholder = false;
  updatePlaceholder();
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
    renderResults(payload);
    renderTechnicalTrace(requestPayload, payload);
    conversationHistory.push({ role: "user", content: message });
    conversationHistory.push({ role: "assistant", content: payload.answer });
    statusPill.textContent = t("ready");
  } catch (error) {
    renderResults({ answer: t("requestFailed"), destinations: [], applied_filters: {}, matched_terms: [] });
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
    appendSummaryCard(payload.answer);

  if (!destinations.length) {
    resultsPanel.hidden = false;
    if (!payload.answer) {
      const emptyCard = document.createElement("article");
      emptyCard.className = "destination-card";
      emptyCard.innerHTML = `
        <h4>${t("noDestinationTitle")}</h4>
        <p class="destination-subtitle">${t("noDestinationBody")}</p>
      `;
      destinationGrid.appendChild(emptyCard);
    }
    return;
  }

  destinations.forEach((destination) => {
    const card = document.createElement("article");
    card.className = "destination-card";
    card.innerHTML = `
      <h4>${destination.destination_name}</h4>
      <p class="destination-subtitle">${destination.destination_country}</p>
      <div class="destination-price">${t("fromEur")} ${Math.round(destination.estimated_from_price_eur)}</div>
      <p class="destination-description">${escapeHtml(destination.description || buildDestinationDescription(destination))}</p>
      <p class="destination-meta">${t("priceCategory")}: ${destination.price_category}</p>
      <p class="destination-tags">${t("tripTags")}: ${destination.trip_tags}</p>
      <p class="destination-tags">${t("bestSeasons")}: ${destination.best_seasons}</p>
    `;
    destinationGrid.appendChild(card);
  });

  resultsPanel.hidden = false;
}

function appendSummaryCard(summaryText) {
  if (!summaryText) {
    return;
  }

  const summaryCard = document.createElement("article");
  summaryCard.className = "summary-card";
  summaryCard.innerHTML = `
    <h4>${t("summaryTitle")}</h4>
    <p>${escapeHtml(summaryText)}</p>
  `;
  destinationGrid.appendChild(summaryCard);
}

function renderTechnicalTrace(requestPayload, responsePayload) {
  requestJson.textContent = prettyJson(requestPayload);
  responseJson.textContent = responsePayload ? prettyJson(responsePayload) : "";
}

function setBusyState(isBusy) {
  sendButton.disabled = isBusy;
  sendButton.classList.toggle("is-loading", isBusy);
  sendButtonLabel.textContent = isBusy ? t("searching") : t("search");
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
      element.setAttribute("placeholder", showPromptPlaceholder ? translations[currentLanguage][key] : "");
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

function updatePlaceholder() {
  messageInput.setAttribute(
    "placeholder",
    showPromptPlaceholder ? t("composerPlaceholder") : "",
  );
}

function buildDestinationDescription(destination) {
  const tags = (destination.trip_tags || "").split("|").filter(Boolean).slice(0, 3);
  const seasons = (destination.best_seasons || "").split("|").filter(Boolean).slice(0, 2);
  const priceMap = {
    budget: {
      en: "This is one of the most budget-friendly options in the current result set.",
      nl: "Dit is een van de meest budgetvriendelijke opties in deze selectie.",
      fr: "C'est l'une des options les plus abordables de cette selection.",
    },
    mid_range: {
      en: "This option balances price and experience nicely for a broad audience.",
      nl: "Deze optie biedt een mooie balans tussen prijs en ervaring.",
      fr: "Cette option offre un bon equilibre entre prix et experience.",
    },
    premium: {
      en: "This is a more premium option with room for a richer trip experience.",
      nl: "Dit is een wat premiumere optie met ruimte voor een rijkere reiservaring.",
      fr: "C'est une option plus premium avec une experience plus riche.",
    },
  };

  const tagText = tags.length ? tags.map(humanizeKey).join(", ") : humanizeKey(destination.price_category || "");
  const seasonText = seasons.length ? seasons.map(humanizeKey).join(" and ") : "";
  const priceText = (priceMap[destination.price_category] || priceMap.mid_range)[currentLanguage] || priceMap.mid_range.en;

  if (currentLanguage === "nl") {
    return `${destination.destination_name} voelt aan als een goede match voor ${tagText}. ${seasonText ? `Vooral sterk in ${seasonText}. ` : ""}${priceText}`;
  }

  if (currentLanguage === "fr") {
    return `${destination.destination_name} convient bien pour un voyage axe sur ${tagText}. ${seasonText ? `Particulierement interessant en ${seasonText}. ` : ""}${priceText}`;
  }

  return `${destination.destination_name} is a strong fit for travelers looking for ${tagText}. ${seasonText ? `It works especially well in ${seasonText}. ` : ""}${priceText}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
