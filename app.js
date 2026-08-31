/**
 * Plant Disease Information Agent - Interactive Frontend Engine
 */

let currentFormattedReport = "";
let autocompleteTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  const inputEl = document.getElementById("disease-input");
  const clearBtn = document.getElementById("btn-clear");

  // Input listeners
  inputEl.addEventListener("input", (e) => {
    const val = e.target.value;
    clearBtn.style.display = val.length > 0 ? "block" : "none";
    handleAutocomplete(val);
  });

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      closeAutocomplete();
      handleSearch();
    }
  });

  // Close autocomplete on click outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".input-wrapper")) {
      closeAutocomplete();
    }
  });

  // Setup drag-and-drop on drop-zone
  const dropZone = document.getElementById("drop-zone");
  if (dropZone) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("dragover");
    });
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        uploadAndDiagnose(e.dataTransfer.files[0]);
      }
    });
  }
});

function switchTab(tab) {
  const tabSearch = document.getElementById("tab-search");
  const tabImage = document.getElementById("tab-image");
  const searchSec = document.getElementById("search-section");
  const imageSec = document.getElementById("image-section");

  if (tab === "search") {
    tabSearch.classList.add("active");
    tabImage.classList.remove("active");
    searchSec.classList.remove("hidden");
    imageSec.classList.add("hidden");
  } else {
    tabImage.classList.add("active");
    tabSearch.classList.remove("active");
    imageSec.classList.remove("hidden");
    searchSec.classList.add("hidden");
  }
}

function selectQuick(diseaseName) {
  switchTab("search");
  const inputEl = document.getElementById("disease-input");
  inputEl.value = diseaseName;
  document.getElementById("btn-clear").style.display = "block";
  closeAutocomplete();
  handleSearch();
}

function clearInput() {
  const inputEl = document.getElementById("disease-input");
  inputEl.value = "";
  document.getElementById("btn-clear").style.display = "none";
  inputEl.focus();
  closeAutocomplete();
  hideResults();
  hideAlert();
}

function closeAutocomplete() {
  const box = document.getElementById("autocomplete-list");
  box.classList.add("hidden");
  box.innerHTML = "";
}

function handleAutocomplete(query) {
  clearTimeout(autocompleteTimer);
  if (!query || query.trim().length < 2) {
    closeAutocomplete();
    return;
  }

  autocompleteTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/diseases/suggest?q=${encodeURIComponent(query.trim())}`);
      if (!res.ok) return;
      const data = await res.json();
      renderAutocomplete(data.suggestions || []);
    } catch (e) {
      console.warn("Autocomplete fetch failed:", e);
    }
  }, 200);
}

function renderAutocomplete(suggestions) {
  const box = document.getElementById("autocomplete-list");
  if (!suggestions || suggestions.length === 0) {
    closeAutocomplete();
    return;
  }

  box.innerHTML = suggestions.map(item => `
    <div class="autocomplete-item" onclick="selectQuick('${escapeHtml(item.name)}')">
      <span class="ac-name">${escapeHtml(item.name)}</span>
      <span class="ac-meta">${escapeHtml(item.plant)} &bull; ${escapeHtml(item.type)}</span>
    </div>
  `).join("");
  box.classList.remove("hidden");
}

async function handleSearch() {
  const inputEl = document.getElementById("disease-input");
  const query = inputEl.value.trim();

  if (!query) {
    showAlert("warning", "Input Required", "Please enter a plant disease name to search.");
    return;
  }

  hideAlert();
  hideResults();
  showLoading(true, "Analyzing Plant Disease Query...", "Searching verified agricultural extension records");

  try {
    const response = await fetch("/api/disease", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ disease: query })
    });

    const data = await response.json();
    showLoading(false);

    if (data.status === "success") {
      renderSuccessResults(data);
    } else if (data.status === "ambiguous") {
      renderAmbiguousAlert(data);
    } else if (data.status === "unknown") {
      renderUnknownAlert(data);
    } else {
      showAlert("error", "Error", data.message || "An unexpected error occurred.");
    }
  } catch (err) {
    showLoading(false);
    showAlert("error", "Network Error", "Unable to connect to the disease agent service. Please verify the backend is running.");
    console.error(err);
  }
}

function renderSuccessResults(data) {
  currentFormattedReport = data.formatted_output || "";

  // Title & Host Meta
  document.getElementById("res-disease-title").textContent = data.disease;
  document.getElementById("res-badge-type").textContent = data.type;
  document.getElementById("res-plant-name").textContent = data.plant;
  document.getElementById("res-query-name").textContent = data.query;

  // Severity Level with Color Coding
  const sevVal = document.getElementById("res-severity-val");
  sevVal.textContent = data.severity;
  sevVal.className = "severity-val";
  if (data.severity.toLowerCase().includes("low")) {
    sevVal.classList.add("sev-low");
  } else if (data.severity.toLowerCase().includes("high")) {
    sevVal.classList.add("sev-high");
  } else {
    sevVal.classList.add("sev-mod");
  }

  // Overview / Description
  document.getElementById("res-description").textContent = data.description;

  // Symptoms
  const symptomsList = document.getElementById("res-symptoms-list");
  symptomsList.innerHTML = (data.symptoms || []).map(s => `<li>${escapeHtml(s)}</li>`).join("");

  // Etiology & Spread
  document.getElementById("res-cause").textContent = data.cause;
  document.getElementById("res-spread").textContent = data.spread;

  // Affected Parts
  const affectedContainer = document.getElementById("res-affected-parts");
  affectedContainer.innerHTML = (data.affected_parts || []).map(p => `<span class="tag-item">${escapeHtml(p)}</span>`).join("");

  // Favorable Conditions
  const conditionsList = document.getElementById("res-conditions-list");
  conditionsList.innerHTML = (data.conditions || []).map(c => `<li>${escapeHtml(c)}</li>`).join("");

  // Treatment / Management
  const treatmentList = document.getElementById("res-treatment-list");
  treatmentList.innerHTML = (data.treatment || []).map(t => `<li>${escapeHtml(t)}</li>`).join("");

  // Prevention
  const preventionList = document.getElementById("res-prevention-list");
  preventionList.innerHTML = (data.prevention || []).map(p => `<li>${escapeHtml(p)}</li>`).join("");

  // Organic Management
  const organicList = document.getElementById("res-organic-list");
  organicList.innerHTML = (data.organic_management || []).map(o => `<li>${escapeHtml(o)}</li>`).join("");

  // Chemical Management
  const chemicalList = document.getElementById("res-chemical-list");
  chemicalList.innerHTML = (data.chemical_management || []).map(c => `<li>${escapeHtml(c)}</li>`).join("");

  // When to Seek Help
  document.getElementById("res-when-help").textContent = data.when_to_seek_help;

  // Sources
  const sourcesList = document.getElementById("res-sources-list");
  sourcesList.innerHTML = (data.sources || []).map(src => `<li class="source-pill">${escapeHtml(src)}</li>`).join("");

  // Disclaimer
  if (data.disclaimer) {
    document.getElementById("res-disclaimer").textContent = data.disclaimer;
  }

  // Raw pre-formatted box
  document.getElementById("raw-formatted-output").textContent = currentFormattedReport;

  // Reveal results
  const resultsContainer = document.getElementById("results-container");
  resultsContainer.classList.remove("hidden");
  resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAmbiguousAlert(data) {
  const alertContainer = document.getElementById("alert-container");
  const matches = data.matches || [];

  const buttonsHtml = matches.map(m => `
    <button class="ambiguity-btn" onclick="selectQuick('${escapeHtml(m)}')">
      🌱 ${escapeHtml(m)}
    </button>
  `).join("");

  alertContainer.innerHTML = `
    <div class="alert-card alert-ambiguous">
      <div class="alert-header">
        <span class="alert-icon">⚠️</span>
        <h3 class="alert-title">Multiple Matches Found</h3>
      </div>
      <p class="alert-message">${escapeHtml(data.message)}</p>
      <div class="ambiguity-options">
        ${buttonsHtml}
      </div>
    </div>
  `;
  alertContainer.classList.remove("hidden");
  alertContainer.scrollIntoView({ behavior: "smooth", block: "center" });
}

function renderUnknownAlert(data) {
  const alertContainer = document.getElementById("alert-container");
  alertContainer.innerHTML = `
    <div class="alert-card alert-unknown">
      <div class="alert-header">
        <span class="alert-icon">🔍</span>
        <h3 class="alert-title">Unknown Disease</h3>
      </div>
      <p class="alert-message">${escapeHtml(data.message)}</p>
    </div>
  `;
  alertContainer.classList.remove("hidden");
  alertContainer.scrollIntoView({ behavior: "smooth", block: "center" });
}

function showAlert(type, title, message) {
  const alertContainer = document.getElementById("alert-container");
  alertContainer.innerHTML = `
    <div class="alert-card alert-${type}">
      <div class="alert-header">
        <span class="alert-icon">${type === 'warning' ? '⚠️' : '❌'}</span>
        <h3 class="alert-title">${escapeHtml(title)}</h3>
      </div>
      <p class="alert-message">${escapeHtml(message)}</p>
    </div>
  `;
  alertContainer.classList.remove("hidden");
}

function hideAlert() {
  const alertContainer = document.getElementById("alert-container");
  alertContainer.classList.add("hidden");
  alertContainer.innerHTML = "";
}

function hideResults() {
  document.getElementById("results-container").classList.add("hidden");
}

function showLoading(show, title = "", desc = "") {
  const loader = document.getElementById("loading-indicator");
  if (show) {
    document.getElementById("loading-step-title").textContent = title;
    document.getElementById("loading-step-desc").textContent = desc;
    loader.classList.remove("hidden");
  } else {
    loader.classList.add("hidden");
  }
}

function copyFormattedReport() {
  if (!currentFormattedReport) return;

  navigator.clipboard.writeText(currentFormattedReport).then(() => {
    const copyBtnText = document.getElementById("copy-btn-text");
    const original = copyBtnText.textContent;
    copyBtnText.textContent = "Copied!";
    setTimeout(() => {
      copyBtnText.textContent = original;
    }, 2000);
  }).catch(err => {
    console.error("Clipboard copy failed", err);
  });
}

function toggleRawView() {
  const rawBox = document.getElementById("raw-formatted-output");
  const toggleBtnText = document.getElementById("raw-toggle-text");
  if (rawBox.classList.contains("hidden")) {
    rawBox.classList.remove("hidden");
    toggleBtnText.textContent = "Hide Plain Text Format";
  } else {
    rawBox.classList.add("hidden");
    toggleBtnText.textContent = "Show Plain Text Format (Requirement 6)";
  }
}

// Image Upload Diagnosis Extension
function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    uploadAndDiagnose(file);
  }
}

async function runSampleImage(sampleName) {
  // Create a synthetic image blob to test the endpoint seamlessly
  const canvas = document.createElement("canvas");
  canvas.width = 100;
  canvas.height = 100;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#2e7d32";
  ctx.fillRect(0, 0, 100, 100);

  canvas.toBlob((blob) => {
    const file = new File([blob], sampleName, { type: "image/jpeg" });
    uploadAndDiagnose(file);
  }, "image/jpeg");
}

async function uploadAndDiagnose(file) {
  showLoading(true, "Classifying Plant Leaf Image...", "Vision model running feature extraction & pathology lookup");
  hideAlert();
  hideResults();

  const preview = document.getElementById("image-preview");
  const previewContainer = document.getElementById("image-preview-container");
  const filenameEl = document.getElementById("image-filename");

  preview.src = URL.createObjectURL(file);
  filenameEl.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
  previewContainer.classList.remove("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/disease/diagnose-image", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    showLoading(false);

    if (data.status === "success" && data.agent_details) {
      // Show confirmation alert of the vision prediction
      showAlert("ambiguous", `Leaf Image Classified: ${data.predicted_disease}`, `${data.message} Loading detailed agricultural treatment profile...`);
      setTimeout(() => {
        hideAlert();
        if (data.agent_details.data) {
          renderSuccessResults(data.agent_details.data);
        } else if (data.agent_details.status === "success") {
          renderSuccessResults(data.agent_details);
        }
      }, 1200);
    } else {
      showAlert("error", "Diagnosis Failed", data.detail || "Could not classify image.");
    }
  } catch (err) {
    showLoading(false);
    showAlert("error", "Upload Error", "Failed to upload and diagnose image.");
    console.error(err);
  }
}

function escapeHtml(text) {
  if (text == null) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
