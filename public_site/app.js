const translations = {
  en: {
    eyebrow: "Candidate-side ATS intelligence",
    headline: "Know if your resume can pass the first screen.",
    lead: "Upload your resume and a job description. We check machine readability, job fit, missing signals, and practical fixes without adding skills you do not have.",
    start: "Start the check",
    workspaceEyebrow: "Private by design",
    workspaceTitle: "Run a focused resume check",
    workspaceLead: "API keys stay server-side. The public screen shows only readiness, results, and recommendations.",
    resumeTitle: "Resume",
    resumeUpload: "Upload PDF or DOCX resume",
    languageLabel: "Detected language correction",
    jdTitle: "Job description",
    jdText: "Paste job description",
    jdUrl: "Or add job URL",
    jdImage: "Or upload screenshot",
    precheck: "Quick precheck",
    analyze: "Analyze fit",
    status: "Status",
    statusIdle: "Ready when you are",
    statusCopy: "Run a short precheck first, then continue to full analysis.",
    resultEyebrow: "Decision summary",
    fixes: "Recommended fixes",
    keywords: "Missing keywords",
    careers: "Adjacent roles to explore",
    copy: "Copy summary",
    download: "Download JSON",
    mirrorEyebrow: "Static mirror",
    mirrorTitle: "Open the secure app to run analysis.",
    mirrorCopy: "This page is a static mirror. Resume analysis runs on the live FastAPI service.",
    openLive: "Open live analyzer",
    footerPrivacy: "Uploaded files are processed by the server for the analysis request.",
    footerKeys: "Provider keys stay server-side and are never sent to the browser.",
  },
  he: {
    eyebrow: "מודיעין ATS לצד המועמד",
    headline: "דע אם קורות החיים שלך עוברים סינון ראשוני.",
    lead: "העלה קורות חיים ותיאור משרה. נבדוק קריאות למערכות ATS, התאמה למשרה, אותות חסרים ותיקונים מעשיים בלי להמציא ניסיון.",
    start: "התחל בדיקה",
    workspaceEyebrow: "פרטיות כברירת מחדל",
    workspaceTitle: "בדיקת קורות חיים ממוקדת",
    workspaceLead: "מפתחות API נשארים בצד השרת. המסך הציבורי מציג רק מוכנות, תוצאה והמלצות.",
    resumeTitle: "קורות חיים",
    resumeUpload: "העלה קובץ PDF או DOCX",
    languageLabel: "תיקון שפה אם הזיהוי לא נכון",
    jdTitle: "תיאור משרה",
    jdText: "הדבק תיאור משרה",
    jdUrl: "או הוסף קישור למשרה",
    jdImage: "או העלה צילום מסך",
    precheck: "בדיקה קצרה",
    analyze: "נתח התאמה",
    status: "סטטוס",
    statusIdle: "מוכן להתחיל",
    statusCopy: "הפעל קודם בדיקה קצרה, ואז המשך לניתוח מלא.",
    resultEyebrow: "סיכום החלטה",
    fixes: "תיקונים מומלצים",
    keywords: "מילות מפתח חסרות",
    careers: "תפקידים סמוכים שכדאי לבדוק",
    copy: "העתק סיכום",
    download: "הורד JSON",
    mirrorEyebrow: "מראה סטטית",
    mirrorTitle: "פתח את האפליקציה המאובטחת כדי להריץ ניתוח.",
    mirrorCopy: "העמוד הזה סטטי. ניתוח קורות החיים רץ בשירות FastAPI החי.",
    openLive: "פתח את המנתח החי",
    footerPrivacy: "קבצים שמועלים מעובדים בצד השרת עבור בקשת הניתוח.",
    footerKeys: "מפתחות provider נשארים בצד השרת ולא נשלחים לדפדפן.",
  },
};

const runtimeConfig = window.SignalCVConfig || {};
const apiBaseUrl = runtimeConfig.API_BASE_URL || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "");
const isStaticMirror = Boolean(runtimeConfig.STATIC_MIRROR);

const form = document.getElementById("analysisForm");
const resumeFile = document.getElementById("resumeFile");
const jdImage = document.getElementById("jdImage");
const jdText = document.getElementById("jdText");
const jdUrl = document.getElementById("jdUrl");
const precheckButton = document.getElementById("precheckButton");
const analyzeButton = document.getElementById("analyzeButton");
const statusTitle = document.getElementById("statusTitle");
const statusCopy = document.getElementById("statusCopy");
const signalVisual = document.getElementById("signalVisual");
const results = document.getElementById("results");
const languageToggle = document.getElementById("languageToggle");
const downloadButton = document.getElementById("downloadResult");
const pagesMirror = document.getElementById("pagesMirror");
const liveAppLink = document.getElementById("liveAppLink");

let currentLanguage = "en";
let lastResult = null;

function setLanguage(language) {
  currentLanguage = language;
  document.documentElement.lang = language === "he" ? "he" : "en";
  document.body.classList.toggle("rtl", language === "he");
  languageToggle.textContent = language === "he" ? "English" : "עברית";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (translations[language][key]) {
      node.textContent = translations[language][key];
    }
  });
}

function setStatus(title, copy, mode = "idle") {
  statusTitle.textContent = title;
  statusCopy.textContent = copy;
  signalVisual.parentElement.classList.toggle("loading", mode === "loading");
  signalVisual.parentElement.classList.toggle("idle", mode === "idle");
}

function buildFormData() {
  const data = new FormData();
  const file = resumeFile.files[0];
  if (file) {
    if (file.name.toLowerCase().endsWith(".pdf")) {
      data.append("pdf_resume", file);
    } else {
      data.append("docx_resume", file);
    }
  }
  if (jdText.value.trim()) {
    data.append("jd_text", jdText.value.trim());
  }
  if (jdUrl.value.trim()) {
    data.append("jd_url", jdUrl.value.trim());
  }
  if (jdImage.files[0]) {
    data.append("jd_image", jdImage.files[0]);
  }
  return data;
}

function validateInputs() {
  if (!resumeFile.files[0]) {
    throw new Error(currentLanguage === "he" ? "צריך להעלות קובץ קורות חיים." : "Upload a resume file first.");
  }
  if (!jdText.value.trim() && !jdUrl.value.trim() && !jdImage.files[0]) {
    throw new Error(currentLanguage === "he" ? "צריך להוסיף תיאור משרה, תמונה או קישור." : "Add a job description, screenshot, or URL.");
  }
}

async function postForm(url) {
  validateInputs();
  const response = await fetch(`${apiBaseUrl}${url}`, {
    method: "POST",
    body: buildFormData(),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed.");
  }
  return payload;
}

function configureStaticMirror() {
  if (!isStaticMirror) return;
  const liveUrl = runtimeConfig.LIVE_APP_URL || "https://ats-resume-analyzer.onrender.com";
  pagesMirror.classList.remove("hidden");
  liveAppLink.href = liveUrl;
  precheckButton.disabled = true;
  analyzeButton.disabled = true;
  setStatus("Static mirror", "Open the live analyzer to upload files and run the check.", "idle");
}

function updateFileLabels() {
  document.getElementById("resumeFileName").textContent = resumeFile.files[0]?.name || "No file selected";
  document.getElementById("jdImageName").textContent = jdImage.files[0]?.name || "Optional";
}

function scoreColor(score) {
  if (score >= 75) return "#62bd83";
  if (score >= 50) return "#efbd62";
  return "#dc6b6b";
}

function renderScores(scores) {
  const labels = {
    parseability_score: "ATS readability",
    keyword_match_score: "Keyword match",
    semantic_match_score: "Semantic fit",
    leadership_alignment_score: "Leadership fit",
    quantified_impact_score: "Impact proof",
    final_ats_score: "Final ATS",
  };
  const scoreBars = document.getElementById("scoreBars");
  scoreBars.innerHTML = "";
  Object.entries(scores).forEach(([key, value]) => {
    const score = Number(value || 0);
    const row = document.createElement("div");
    row.className = "score-bar";
    row.innerHTML = `
      <strong>${labels[key] || key}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.max(0, Math.min(100, score))}%; background:${scoreColor(score)}"></div></div>
      <span>${score.toFixed(1)}</span>
    `;
    scoreBars.appendChild(row);
  });
}

function renderList(elementId, items, emptyText) {
  const list = document.getElementById(elementId);
  list.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    list.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderKeywords(keywords) {
  const holder = document.getElementById("keywords");
  holder.innerHTML = "";
  if (!keywords || keywords.length === 0) {
    const span = document.createElement("span");
    span.textContent = currentLanguage === "he" ? "לא נמצאו פערים מרכזיים" : "No major gaps";
    holder.appendChild(span);
    return;
  }
  keywords.forEach((keyword) => {
    const span = document.createElement("span");
    span.textContent = keyword;
    holder.appendChild(span);
  });
}

function renderResult(payload) {
  lastResult = payload;
  const score = Number(payload.final_ats_score || 0);
  document.getElementById("verdict").textContent = payload.verdict || "-";
  document.getElementById("summary").textContent = payload.summary || "";
  renderApiStatus(payload);
  const ring = document.getElementById("scoreRing");
  ring.style.setProperty("--score", `${Math.max(0, Math.min(100, score))}%`);
  document.getElementById("scoreValue").textContent = score.toFixed(0);
  renderScores(payload.scores || {});
  renderList("recommendations", currentLanguage === "he" ? payload.hebrew_recommendations : payload.recommendations, "No recommendations returned.");
  renderKeywords(payload.missing_keywords || []);
  renderList("careerIdeas", payload.career_suggestions, "Career suggestions will appear after analysis.");
  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderApiStatus(payload) {
  const holder = document.getElementById("apiStatus");
  const usage = payload.token_usage || {};
  const aiComplete = payload.ai_status === "completed";
  holder.innerHTML = `
    <span class="ok">Core analysis completed</span>
    <span class="${payload.analysis_mode === "local_no_api" ? "ok" : aiComplete ? "ok" : "warn"}">${payload.analysis_mode === "local_no_api" ? "No external API used" : aiComplete ? "AI insights completed" : "AI insights skipped"}</span>
    <span>API tokens: ${usage.total_tokens || 0}</span>
    <span>Model: ${usage.model || "hidden"}</span>
  `;
  if (payload.ai_note) {
    const note = document.createElement("span");
    note.className = "warn";
    note.textContent = payload.ai_note;
    holder.appendChild(note);
  }
}

function resultText() {
  if (!lastResult) return "";
  const lines = [
    `Verdict: ${lastResult.verdict}`,
    `ATS score: ${Number(lastResult.final_ats_score || 0).toFixed(1)}/100`,
    lastResult.summary || "",
    "",
    "Missing keywords:",
    (lastResult.missing_keywords || []).join(", ") || "None",
    "",
    "Recommended fixes:",
    ...(lastResult.recommendations || []).map((item) => `- ${item}`),
    "",
    "Adjacent roles:",
    ...(lastResult.career_suggestions || []).map((item) => `- ${item}`),
  ];
  return lines.join("\n");
}

resumeFile.addEventListener("change", updateFileLabels);
jdImage.addEventListener("change", updateFileLabels);

languageToggle.addEventListener("click", () => {
  setLanguage(currentLanguage === "en" ? "he" : "en");
});

precheckButton.addEventListener("click", async () => {
  try {
    setStatus("Checking readiness", "Reading the resume and validating the job input.", "loading");
    const payload = await postForm("/public/precheck");
    const details = payload.checks.map((check) => `${check.label}: ${check.status}`).join(" · ");
    setStatus(payload.ready ? "Ready for full analysis" : "Precheck needs attention", `${payload.recommended_action} ${details}`, "idle");
  } catch (error) {
    setStatus("Precheck failed", error.message, "idle");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    analyzeButton.disabled = true;
    setStatus("Analyzing resume fit", "Understanding the role, checking ATS signals, and building practical recommendations.", "loading");
    const payload = await postForm("/public/analyze");
    renderResult(payload);
    setStatus("Analysis complete", "Review the decision summary and the first fixes before rewriting anything.", "idle");
  } catch (error) {
    setStatus("Analysis could not finish", error.message, "idle");
  } finally {
    analyzeButton.disabled = false;
  }
});

document.getElementById("copyResult").addEventListener("click", async () => {
  if (!lastResult) return;
  await navigator.clipboard.writeText(resultText());
  document.getElementById("copyResult").textContent = currentLanguage === "he" ? "הועתק" : "Copied";
  setTimeout(() => {
    document.getElementById("copyResult").textContent = translations[currentLanguage].copy;
  }, 1400);
});

downloadButton.addEventListener("click", () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ats_analysis_report.json";
  link.click();
  URL.revokeObjectURL(url);
});

setLanguage("en");
configureStaticMirror();
