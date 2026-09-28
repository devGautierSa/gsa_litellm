const API_KEY_STORAGE = "gsa_litellm_app_api_key";

function getApiKey() {
  return localStorage.getItem(API_KEY_STORAGE) || "";
}

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const apiKey = getApiKey();
  if (apiKey) headers["X-App-Api-Key"] = apiKey;

  const response = await fetch(path, { ...options, headers });
  const text = await response.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error(
        "401 Unauthorized : renseignez la clé API du serveur en haut de page (X-App-Api-Key) et cliquez sur Enregistrer."
      );
    }
    throw new Error(typeof body === "string" ? body : JSON.stringify(body, null, 2));
  }
  return body;
}

function createJsonNode(key, value) {
  const wrapper = document.createElement("div");
  wrapper.className = "json-node";

  const isObject = value !== null && typeof value === "object";
  const line = document.createElement("div");
  line.className = "json-line";

  const toggle = document.createElement("span");
  toggle.className = isObject ? "json-toggle" : "json-spacer";
  toggle.textContent = isObject ? "▾" : "";
  line.appendChild(toggle);

  if (key !== null) {
    const keySpan = document.createElement("span");
    keySpan.className = "json-key";
    keySpan.textContent = `${key}: `;
    line.appendChild(keySpan);
  }

  if (isObject) {
    const entries = Object.entries(value);
    const meta = document.createElement("span");
    meta.className = "json-meta";
    meta.textContent = Array.isArray(value) ? `Array(${entries.length})` : `Object(${entries.length})`;
    line.appendChild(meta);

    const children = document.createElement("div");
    children.className = "json-children";
    entries.forEach(([childKey, childValue]) => children.appendChild(createJsonNode(childKey, childValue)));

    line.classList.add("json-line-expandable");
    line.addEventListener("click", (event) => {
      event.stopPropagation();
      const collapsed = children.classList.toggle("collapsed");
      toggle.textContent = collapsed ? "▸" : "▾";
    });

    wrapper.append(line, children);
  } else {
    const valueSpan = document.createElement("span");
    valueSpan.className = `json-value json-${value === null ? "null" : typeof value}`;
    valueSpan.textContent = JSON.stringify(value);
    line.appendChild(valueSpan);
    wrapper.appendChild(line);
  }

  return wrapper;
}

function renderJsonTree(container, data) {
  container.innerHTML = "";
  if (data !== null && typeof data === "object") {
    const entries = Object.entries(data);
    if (entries.length === 0) {
      container.textContent = Array.isArray(data) ? "[]" : "{}";
      return;
    }
    entries.forEach(([key, value]) => container.appendChild(createJsonNode(key, value)));
  } else {
    container.appendChild(createJsonNode(null, data));
  }
}

function show(outputId, data) {
  const container = document.getElementById(outputId);
  if (typeof data === "string") {
    container.textContent = data;
    return;
  }
  renderJsonTree(container, data);
}

function showError(outputId, error) {
  document.getElementById(outputId).textContent = `Erreur: ${error.message}`;
}

function formToObject(form, { numberFields = [], listFields = [] } = {}) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const key of Object.keys(data)) {
    if (data[key] === "") delete data[key];
  }
  for (const field of numberFields) {
    if (data[field] !== undefined) data[field] = Number(data[field]);
  }
  for (const field of listFields) {
    if (data[field] !== undefined) {
      data[field] = data[field].split(",").map((s) => s.trim()).filter(Boolean);
    }
  }
  return data;
}

// --- Onglets ---
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// --- Clé API du serveur ---
document.getElementById("app-api-key").value = getApiKey();
document.getElementById("save-api-key").addEventListener("click", () => {
  const value = document.getElementById("app-api-key").value;
  localStorage.setItem(API_KEY_STORAGE, value);
  alert("Clé enregistrée localement.");
});

// --- Modèles ---
document.querySelectorAll("[data-action='list-models']").forEach((b) =>
  b.addEventListener("click", async () => {
    try {
      show("output-models", await apiFetch("/api/models"));
    } catch (e) {
      showError("output-models", e);
    }
  })
);
document.querySelector("[data-action='model-info']").addEventListener("click", async () => {
  try {
    show("output-models", await apiFetch("/api/models/info"));
  } catch (e) {
    showError("output-models", e);
  }
});
document.getElementById("form-add-model").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target);
  const payload = {
    model_name: data.model_name,
    litellm_params: {
      model: data.model,
      ...(data.api_key ? { api_key: data.api_key } : {}),
      ...(data.api_base ? { api_base: data.api_base } : {}),
    },
  };
  try {
    show("output-models", await apiFetch("/api/models", { method: "POST", body: JSON.stringify(payload) }));
  } catch (e2) {
    showError("output-models", e2);
  }
});
document.getElementById("form-delete-model").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { model_id } = formToObject(e.target);
  try {
    show("output-models", await apiFetch(`/api/models/${encodeURIComponent(model_id)}`, { method: "DELETE" }));
  } catch (e2) {
    showError("output-models", e2);
  }
});

// --- Chat ---
document.getElementById("form-chat").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { model, message } = formToObject(e.target);
  const payload = { model, messages: [{ role: "user", content: message }] };
  try {
    show("output-chat", await apiFetch("/api/chat/completions", { method: "POST", body: JSON.stringify(payload) }));
  } catch (e2) {
    showError("output-chat", e2);
  }
});

// --- Clés API ---
document.querySelector("[data-action='list-keys']").addEventListener("click", async () => {
  try {
    show("output-keys", await apiFetch("/api/keys"));
  } catch (e) {
    showError("output-keys", e);
  }
});
document.getElementById("form-generate-key").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target, { numberFields: ["max_budget"], listFields: ["models"] });
  try {
    show("output-keys", await apiFetch("/api/keys/generate", { method: "POST", body: JSON.stringify(data) }));
  } catch (e2) {
    showError("output-keys", e2);
  }
});
document.getElementById("form-delete-key").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target, { listFields: ["keys"] });
  try {
    show("output-keys", await apiFetch("/api/keys/delete", { method: "POST", body: JSON.stringify(data) }));
  } catch (e2) {
    showError("output-keys", e2);
  }
});

// --- Utilisateurs ---
document.querySelector("[data-action='list-users']").addEventListener("click", async () => {
  try {
    show("output-users", await apiFetch("/api/users"));
  } catch (e) {
    showError("output-users", e);
  }
});
document.getElementById("form-create-user").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target, { numberFields: ["max_budget"] });
  try {
    show("output-users", await apiFetch("/api/users", { method: "POST", body: JSON.stringify(data) }));
  } catch (e2) {
    showError("output-users", e2);
  }
});

// --- Équipes ---
document.querySelector("[data-action='list-teams']").addEventListener("click", async () => {
  try {
    show("output-teams", await apiFetch("/api/teams"));
  } catch (e) {
    showError("output-teams", e);
  }
});
document.getElementById("form-create-team").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target, { numberFields: ["max_budget"] });
  try {
    show("output-teams", await apiFetch("/api/teams", { method: "POST", body: JSON.stringify(data) }));
  } catch (e2) {
    showError("output-teams", e2);
  }
});

// --- Dépenses ---
document.querySelector("[data-action='global-spend']").addEventListener("click", async () => {
  try {
    show("output-spend", await apiFetch("/api/spend/global"));
  } catch (e) {
    showError("output-spend", e);
  }
});
document.querySelector("[data-action='spend-logs']").addEventListener("click", async () => {
  try {
    show("output-spend", await apiFetch("/api/spend/logs"));
  } catch (e) {
    showError("output-spend", e);
  }
});

// --- Prompts ---
document.querySelector("[data-action='list-prompts']").addEventListener("click", async () => {
  try {
    show("output-prompts", await apiFetch("/api/prompts"));
  } catch (e) {
    showError("output-prompts", e);
  }
});
document.getElementById("form-create-prompt").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target, { listFields: ["variables"] });
  try {
    show("output-prompts", await apiFetch("/api/prompts", { method: "POST", body: JSON.stringify(data) }));
  } catch (e2) {
    showError("output-prompts", e2);
  }
});
document.getElementById("form-run-prompt").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = formToObject(e.target);
  let variables = {};
  if (data.variables_json) {
    try {
      variables = JSON.parse(data.variables_json);
    } catch {
      showError("output-prompts", new Error("JSON de variables invalide"));
      return;
    }
  }
  const payload = { variables, ...(data.model ? { model: data.model } : {}) };
  try {
    show(
      "output-prompts",
      await apiFetch(`/api/prompts/${encodeURIComponent(data.prompt_id)}/run`, {
        method: "POST",
        body: JSON.stringify(payload),
      })
    );
  } catch (e2) {
    showError("output-prompts", e2);
  }
});
