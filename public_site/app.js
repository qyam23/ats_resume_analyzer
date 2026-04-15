const translations = {
  en: {
    eyebrow: "ATS Visibility + Job Fit",
    headline: "Find out if your resume will be found.",
    lead: "Upload a resume and a target job. We test ATS readability, recruiter search visibility, role fit, missing signals, and truthful copy-ready fixes.",
    start: "Start private check",
    proofAts: "ATS visibility",
    proofFit: "Job-fit decision",
    proofLocal: "Local AI ready",
    gateEyebrow: "Private access",
    gateTitle: "Enter the site password",
    gateLead: "This private phase uses server-side API enhancement. Keys and passwords are never exposed to the browser.",
    gatePlaceholder: "Password",
    gateSubmit: "Unlock analyzer",
    logout: "Lock session",
    workspaceEyebrow: "Decision-first workspace",
    workspaceTitle: "Run a focused ATS visibility check",
    workspaceLead: "The core ATS engine runs deterministically first. AI is used only for wording and explanation when available.",
    runtimeLocal: "Local runtime",
    runtimeFastapi: "FastAPI on localhost",
    runtimeLlm: "Local LLM enhancement if available",
    runtimeSecrets: "No browser-side secrets",
    stageInput: "Inputs",
    stageInputHint: "Resume and job target",
    stageParse: "Parse",
    stageParseHint: "ATS readability",
    stageMatch: "Match",
    stageMatchHint: "Visibility and fit",
    stageRewrite: "Rewrite",
    stageRewriteHint: "Local AI if reachable",
    resumeTitle: "Resume",
    resumeUpload: "Upload PDF or DOCX resume",
    languageLabel: "Language hint",
    jdTitle: "Target job",
    jdText: "Paste job description",
    jdUrl: "Or add job URL",
    jdImage: "Or upload screenshot",
    precheck: "Quick precheck",
    analyze: "Analyze visibility",
    status: "Status",
    statusIdle: "Locked until inputs are ready",
    statusCopy: "Unlock the analyzer, upload a resume, add the job, then run the precheck.",
    resultEyebrow: "Decision",
    fixes: "Fix now",
    rewrites: "AI rewrite suggestions",
    keywords: "Missing signals",
    careers: "Adjacent roles",
    atsSees: "What ATS sees",
    recruiterSees: "What recruiter sees",
    copy: "Copy report",
    download: "Download JSON",
    mirrorEyebrow: "Static mirror",
    mirrorTitle: "Open the secure app to run analysis.",
    mirrorCopy: "This page is static. Resume analysis runs only on the live FastAPI service.",
    openLive: "Open live analyzer",
    footerPrivacy: "Files are processed server-side for the current analysis request.",
    footerKeys: "Private API keys stay server-side. Hugging Face remains architecture-ready for a later phase.",
  },
  he: {
    eyebrow: "נראות ATS + התאמה למשרה",
    headline: "בדוק אם קורות החיים שלך יימצאו.",
    lead: "העלה קורות חיים ומשרה יעד. נבדוק קריאות ל-ATS, נראות בחיפוש מגייסים, התאמה לתפקיד, אותות חסרים ותיקונים אמיתיים שאפשר להעתיק.",
    start: "התחל בדיקה פרטית",
    proofAts: "נראות ATS",
    proofFit: "החלטת התאמה",
    proofLocal: "AI מקומי מוכן",
    gateEyebrow: "גישה פרטית",
    gateTitle: "הכנס סיסמת אתר",
    gateLead: "בשלב הפרטי הזה שיפור AI רץ בצד השרת בלבד. מפתחות וסיסמאות לא נחשפים לדפדפן.",
    gatePlaceholder: "סיסמה",
    gateSubmit: "פתח את המנתח",
    logout: "נעל סשן",
    workspaceEyebrow: "מרחב החלטה תחילה",
    workspaceTitle: "בדיקת נראות ATS ממוקדת",
    workspaceLead: "מנוע ה-ATS הדטרמיניסטי רץ ראשון. AI משמש רק לניסוח והסבר כאשר הוא זמין.",
    runtimeLocal: "ריצה לוקאלית",
    runtimeFastapi: "FastAPI על localhost",
    runtimeLlm: "שכבת AI מקומית אם זמינה",
    runtimeSecrets: "אין סודות בדפדפן",
    stageInput: "קלט",
    stageInputHint: "קורות חיים ומשרה",
    stageParse: "פענוח",
    stageParseHint: "קריאות ל-ATS",
    stageMatch: "התאמה",
    stageMatchHint: "נראות והתאמה",
    stageRewrite: "ניסוח",
    stageRewriteHint: "AI מקומי אם זמין",
    resumeTitle: "קורות חיים",
    resumeUpload: "העלה קובץ PDF או DOCX",
    languageLabel: "רמז שפה",
    jdTitle: "משרת יעד",
    jdText: "הדבק תיאור משרה",
    jdUrl: "או הוסף קישור למשרה",
    jdImage: "או העלה צילום מסך",
    precheck: "בדיקה קצרה",
    analyze: "נתח נראות",
    status: "סטטוס",
    statusIdle: "נעול עד שהקלט מוכן",
    statusCopy: "פתח את המנתח, העלה קורות חיים, הוסף משרה והריץ בדיקה קצרה.",
    resultEyebrow: "החלטה",
    fixes: "לתקן עכשיו",
    rewrites: "הצעות ניסוח AI",
    keywords: "אותות חסרים",
    careers: "תפקידים סמוכים",
    atsSees: "מה ATS רואה",
    recruiterSees: "מה מגייס רואה",
    copy: "העתק דוח",
    download: "הורד JSON",
    mirrorEyebrow: "מראה סטטית",
    mirrorTitle: "פתח את האפליקציה המאובטחת כדי להריץ ניתוח.",
    mirrorCopy: "העמוד הזה סטטי. ניתוח קורות חיים רץ רק בשירות FastAPI החי.",
    openLive: "פתח מנתח חי",
    footerPrivacy: "קבצים מעובדים בצד השרת עבור בקשת הניתוח הנוכחית.",
    footerKeys: "מפתחות API פרטיים נשארים בצד השרת. Hugging Face נשאר מוכן ארכיטקטונית לשלב עתידי.",
  },
};

const runtimeConfig = window.SignalCVConfig || {};
const apiBaseUrl = runtimeConfig.API_BASE_URL || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "");
const isStaticMirror = Boolean(runtimeConfig.STATIC_MIRROR);

const form = document.getElementById("analysisForm");
const authGate = document.getElementById("authGate");
const loginForm = document.getElementById("loginForm");
const passwordInput = document.getElementById("sitePassword");
const gateError = document.getElementById("gateError");
const logoutButton = document.getElementById("logoutButton");
const analyzerSection = document.getElementById("analyzer");
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
const runtimeStrip = document.getElementById("runtimeStrip");

let currentLanguage = "en";
let lastResult = null;

function t(key) {
  return translations[currentLanguage][key] || translations.en[key] || key;
}

function setLanguage(language) {
  currentLanguage = language;
  document.documentElement.lang = language === "he" ? "he" : "en";
  document.body.classList.toggle("rtl", language === "he");
  languageToggle.textContent = language === "he" ? "English" : "עברית";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
}

function setStatus(title, copy, mode = "idle") {
  statusTitle.textContent = title;
  statusCopy.textContent = copy;
  signalVisual.parentElement.classList.toggle("loading", mode === "loading");
  signalVisual.parentElement.classList.toggle("idle", mode === "idle");
}

function setStage(stage) {
  const order = ["input", "parse", "match", "rewrite"];
  const activeIndex = Math.max(0, order.indexOf(stage));
  document.querySelectorAll(".progress-step").forEach((node) => {
    const index = order.indexOf(node.dataset.stage);
    node.classList.toggle("active", index === activeIndex);
    node.classList.toggle("done", index >= 0 && index < activeIndex);
  });
}

async function refreshAuth() {
  if (isStaticMirror) return;
  const response = await fetch(`${apiBaseUrl}/auth/status`, { credentials: "same-origin" });
  const payload = await response.json();
  const authenticated = Boolean(payload.authenticated);
  authGate.classList.toggle("hidden", authenticated || !payload.auth_enabled);
  analyzerSection.classList.toggle("locked", !authenticated);
  logoutButton.classList.toggle("hidden", !authenticated || !payload.auth_enabled);
  if (authenticated) refreshRuntimeStatus();
}

async function refreshRuntimeStatus() {
  try {
    const response = await fetch(`${apiBaseUrl}/public/runtime-status`, { credentials: "same-origin" });
    if (!response.ok) return;
    const payload = await response.json();
    runtimeStrip.innerHTML = `
      <span>${currentLanguage === "he" ? "סביבה" : "Runtime"}: ${payload.runtime || "local"}</span>
      <span>${currentLanguage === "he" ? "ליבה" : "Core"}: ${payload.deterministic_core || "ready"}</span>
      <span class="${payload.provider_available ? "chip-ok" : "chip-warn"}">${currentLanguage === "he" ? "AI מקומי" : "Local AI"}: ${payload.provider_available ? (currentLanguage === "he" ? "מחובר" : "connected") : (currentLanguage === "he" ? "לא זמין" : "not reachable")}</span>
      <span>${currentLanguage === "he" ? "מודל" : "Model"}: ${payload.model || "local"}</span>
    `;
  } catch (_) {
    runtimeStrip.innerHTML = `
      <span>${currentLanguage === "he" ? "סביבה: לוקאלית" : "Runtime: local"}</span>
      <span>${currentLanguage === "he" ? "ליבה: מוכנה" : "Core: ready"}</span>
      <span class="chip-warn">${currentLanguage === "he" ? "AI מקומי: לא נבדק" : "Local AI: not checked"}</span>
      <span>${currentLanguage === "he" ? "אין סודות בדפדפן" : "No browser-side secrets"}</span>
    `;
  }
}

function buildFormData() {
  const data = new FormData();
  const file = resumeFile.files[0];
  if (file) {
    data.append(file.name.toLowerCase().endsWith(".pdf") ? "pdf_resume" : "docx_resume", file);
  }
  if (jdText.value.trim()) data.append("jd_text", jdText.value.trim());
  if (jdUrl.value.trim()) data.append("jd_url", jdUrl.value.trim());
  if (jdImage.files[0]) data.append("jd_image", jdImage.files[0]);
  return data;
}

function validateInputs() {
  if (!resumeFile.files[0]) throw new Error(currentLanguage === "he" ? "צריך להעלות קובץ קורות חיים." : "Upload a resume file first.");
  if (!jdText.value.trim() && !jdUrl.value.trim() && !jdImage.files[0]) {
    throw new Error(currentLanguage === "he" ? "צריך להוסיף תיאור משרה, תמונה או קישור." : "Add a job description, screenshot, or URL.");
  }
}

async function postForm(url) {
  validateInputs();
  const response = await fetch(`${apiBaseUrl}${url}`, {
    method: "POST",
    body: buildFormData(),
    credentials: "same-origin",
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Request failed.");
  return payload;
}

function configureStaticMirror() {
  if (!isStaticMirror) return;
  const liveUrl = runtimeConfig.LIVE_APP_URL || "https://qyam23-ats-resume-analyzer.hf.space";
  pagesMirror.classList.remove("hidden");
  liveAppLink.href = liveUrl;
  authGate.classList.add("hidden");
  analyzerSection.classList.add("locked");
  precheckButton.disabled = true;
  analyzeButton.disabled = true;
  setStatus("Static mirror", "Open the live analyzer to upload files and run the check.", "idle");
}

function updateFileLabels() {
  document.getElementById("resumeFileName").textContent = resumeFile.files[0]?.name || (currentLanguage === "he" ? "לא נבחר קובץ" : "No file selected");
  document.getElementById("jdImageName").textContent = jdImage.files[0]?.name || (currentLanguage === "he" ? "אופציונלי" : "Optional");
}

function scoreColor(score) {
  if (score >= 75) return "#5fbf8f";
  if (score >= 50) return "#e4b956";
  return "#de716e";
}

function renderScores(scores, payload) {
  const labels = {
    visibility_score: "Visibility",
    recruiter_match_score: "Recruiter search",
    parseability_score: "ATS parse",
    keyword_match_score: "Keywords",
    semantic_match_score: "Semantic fit",
    leadership_alignment_score: "Leadership",
    final_ats_score: "Final ATS",
  };
  const merged = {
    visibility_score: payload.visibility_score,
    recruiter_match_score: payload.recruiter_match_score,
    ...scores,
  };
  const scoreBars = document.getElementById("scoreBars");
  scoreBars.innerHTML = "";
  Object.entries(merged).forEach(([key, value]) => {
    if (!Object.prototype.hasOwnProperty.call(labels, key)) return;
    const score = Number(value || 0);
    const row = document.createElement("div");
    row.className = "score-bar";
    row.innerHTML = `
      <strong>${labels[key]}</strong>
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
  const values = keywords && keywords.length ? keywords : [currentLanguage === "he" ? "אין פער מרכזי ברור" : "No major gap"];
  values.forEach((keyword) => {
    const span = document.createElement("span");
    span.textContent = keyword;
    holder.appendChild(span);
  });
}

function renderCompatibility(scores) {
  const holder = document.getElementById("compatibilityScores");
  holder.innerHTML = "";
  if (!scores || Object.keys(scores).length === 0) {
    holder.textContent = "Compatibility estimates will appear after analysis.";
    return;
  }
  const labels = {
    workday_like: "Workday-like",
    greenhouse_like: "Greenhouse-like",
    legacy_parser_like: "Legacy parser",
    israeli_ats_like: "Israeli ATS-like",
  };
  Object.entries(scores).forEach(([key, value]) => {
    const row = document.createElement("div");
    const score = Number(value || 0);
    row.innerHTML = `<span>${labels[key] || key}</span><strong>${score.toFixed(1)}</strong>`;
    holder.appendChild(row);
  });
}

function firstItems(values, fallback, limit = 3) {
  const clean = (values || [])
    .filter(Boolean)
    .map((item) => String(item).trim())
    .filter(Boolean);
  return (clean.length ? clean : fallback).slice(0, limit);
}

function visibilityProblemText(visibility) {
  if (visibility < 45) return "You are not being found in recruiter searches for this role.";
  if (visibility < 70) return "You are partially visible, but key recruiter search signals are still weak.";
  return "You are visible for this role; focus on sharper positioning and stronger proof.";
}

function renderCoach(payload) {
  const holder = document.getElementById("coachMessages");
  const visibility = Number(payload.visibility_score || 0);
  const keywordCount = ((payload.missing_signals && payload.missing_signals.keywords) || payload.missing_keywords || []).length;
  const messages = [
    { side: "assistant", text: "I analyzed your resume for this role." },
    { side: "assistant", text: visibility < 55 ? "The main issue is low visibility." : "The core fit is visible, but the positioning can be sharper." },
    { side: "user", text: keywordCount ? `I found ${keywordCount} missing recruiter search signals.` : "I did not find a major keyword gap." },
    { side: "assistant", text: "Let’s fix this step by step." },
  ];
  holder.innerHTML = "";
  messages.forEach((message, index) => {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${message.side}`;
    bubble.style.setProperty("--delay", `${index * 80}ms`);
    bubble.textContent = message.text;
    holder.appendChild(bubble);
  });
}

function renderWhyNotFound(payload) {
  const holder = document.getElementById("whyNotFound");
  const keywords = (payload.missing_signals && payload.missing_signals.keywords) || payload.missing_keywords || [];
  const reasons = firstItems(
    (payload.missing_signals && payload.missing_signals.why_not_found) || payload.why_not_found,
    [
      `Missing keyword: ${keywords[0] || "interpret technical documentation"}`,
      "Weak title alignment",
      "Low recruiter search coverage",
    ],
    3
  );
  holder.innerHTML = "";
  reasons.forEach((reason) => {
    const li = document.createElement("li");
    li.textContent = reason;
    holder.appendChild(li);
  });
}

function updateFixProgress() {
  const steps = Array.from(document.querySelectorAll(".fix-step"));
  const applied = steps.filter((step) => step.classList.contains("applied")).length;
  const total = steps.length || 3;
  const label = document.getElementById("fixProgressLabel");
  const fill = document.getElementById("fixProgressFill");
  if (label) label.textContent = `${applied} of ${total} fixes applied`;
  if (fill) fill.style.width = `${Math.round((applied / total) * 100)}%`;
}

function renderFixEngine(payload) {
  const holder = document.getElementById("fixSteps");
  const keywords = (payload.missing_signals && payload.missing_signals.keywords) || payload.missing_keywords || [];
  const fixes = [
    {
      title: "Step 1: Add keyword",
      detail: keywords[0] ? `Add “${keywords[0]}” only where it is truthful and supported by your experience.` : "Add the strongest missing role keyword where it is truthful.",
    },
    {
      title: "Step 2: Improve title",
      detail: "Align the resume headline with the role level recruiters are searching for.",
    },
    {
      title: "Step 3: Improve search phrases",
      detail: "Add 2-3 exact recruiter phrases in summary, skills, and achievement bullets.",
    },
  ];
  holder.innerHTML = "";
  fixes.forEach((fix, index) => {
    const step = document.createElement("article");
    step.className = "fix-step";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `fix-step-${index}`;
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = fix.title;
    const detail = document.createElement("p");
    detail.textContent = fix.detail;
    copy.append(title, detail);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "secondary-button apply-fix";
    button.textContent = "Apply";
    const markApplied = () => {
      checkbox.checked = true;
      step.classList.add("applied");
      button.textContent = "Applied";
      updateFixProgress();
    };
    checkbox.addEventListener("change", () => {
      step.classList.toggle("applied", checkbox.checked);
      button.textContent = checkbox.checked ? "Applied" : "Apply";
      updateFixProgress();
    });
    button.addEventListener("click", markApplied);
    step.append(checkbox, copy, button);
    holder.appendChild(step);
  });
  updateFixProgress();
}

function renderRewritePremium(payload) {
  const holder = document.getElementById("rewritePreview");
  const rewrites = firstItems(
    payload.rewrite_suggestions,
    payload.top_fixes || payload.recommendations || ["Rewrite the summary around leadership, measurable outcomes, and exact role keywords."],
    3
  );
  holder.innerHTML = "";
  rewrites.forEach((rewrite, index) => {
    const row = document.createElement("div");
    row.className = index === 0 ? "rewrite-row" : "rewrite-row locked";
    const label = document.createElement("span");
    label.textContent = index === 0 ? "Free preview" : "Locked";
    const text = document.createElement("p");
    text.textContent = rewrite;
    row.append(label, text);
    holder.appendChild(row);
  });
}

function renderBeforeAfter(payload) {
  const holder = document.getElementById("beforeAfter");
  const before = Number(payload.visibility_score || 0);
  const uplift = before < 45 ? 14 : before < 70 ? 9 : 5;
  const after = Math.min(100, before + uplift);
  holder.innerHTML = "";
  [
    { label: "Before", value: before, tone: "before" },
    { label: "After fix", value: after, tone: "after" },
  ].forEach((item) => {
    const panel = document.createElement("div");
    panel.className = `simulation-side ${item.tone}`;
    panel.innerHTML = `
      <span>${item.label}</span>
      <strong>Visibility: ${item.value.toFixed(0)}</strong>
      <div class="simulation-track"><div style="width:${Math.max(0, Math.min(100, item.value))}%"></div></div>
    `;
    holder.appendChild(panel);
  });
}

function renderJobSearchPlan(payload) {
  const holder = document.getElementById("jobSearchPlan");
  const roles = firstItems(payload.career_suggestions, ["Engineering Manager", "Technical Operations Manager", "Project Engineering Manager"], 3);
  const items = [
    `LinkedIn query: ${roles[0]} + operations + engineering`,
    `Target titles: ${roles.join(", ")}`,
    "Filters: posted this week, mid-senior, engineering operations",
  ];
  holder.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "locked-row";
    row.textContent = item;
    holder.appendChild(row);
  });
}

function renderResult(payload) {
  lastResult = payload;
  const score = Number(payload.final_ats_score || 0);
  const visibility = Number(payload.visibility_score || 0);
  document.getElementById("decision").textContent = payload.decision || payload.verdict || "-";
  document.getElementById("verdict").textContent = payload.verdict || "-";
  document.getElementById("summary").textContent = payload.summary || "";
  document.getElementById("mainProblemText").textContent = visibilityProblemText(visibility);
  document.getElementById("visibilityValue").textContent = visibility.toFixed(1);
  document.getElementById("visibilityFill").style.width = `${Math.max(0, Math.min(100, visibility))}%`;
  document.getElementById("parseValue").textContent = Number(payload.ats_parse_score || 0).toFixed(1);
  renderApiStatus(payload);
  const ring = document.getElementById("scoreRing");
  ring.style.setProperty("--score", `${Math.max(0, Math.min(100, score))}%`);
  document.getElementById("scoreValue").textContent = score.toFixed(0);
  renderScores(payload.scores || {}, payload);
  renderList("recommendations", payload.top_fixes || payload.recommendations, "No recommendations returned.");
  renderKeywords((payload.missing_signals && payload.missing_signals.keywords) || payload.missing_keywords || []);
  renderList("atsSeen", payload.what_ats_sees, "ATS view will appear after analysis.");
  renderList("recruiterSeen", payload.what_recruiter_sees, "Recruiter view will appear after analysis.");
  renderCompatibility(payload.compatibility_scores || {});
  renderCoach(payload);
  renderWhyNotFound(payload);
  renderFixEngine(payload);
  renderRewritePremium(payload);
  renderBeforeAfter(payload);
  renderJobSearchPlan(payload);
  renderList("careerIdeas", firstItems(payload.career_suggestions, ["Engineering Manager", "Head of Engineering Operations", "Technical Operations Manager"], 5), "Career suggestions will appear after analysis.");
  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderApiStatus(payload) {
  const holder = document.getElementById("apiStatus");
  const usage = payload.token_usage || {};
  const aiComplete = payload.ai_status === "completed";
  holder.innerHTML = `
    <span class="ok">Core ATS completed</span>
    <span class="${aiComplete ? "ok" : "warn"}">${aiComplete ? "Private AI enhancement completed" : "AI enhancement skipped"}</span>
    <span>Tokens: ${usage.total_tokens || 0}</span>
    <span>Model: ${usage.model || "server-side"}</span>
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
  return [
    `Decision: ${lastResult.decision || ""}`,
    `Verdict: ${lastResult.verdict}`,
    `ATS score: ${Number(lastResult.final_ats_score || 0).toFixed(1)}/100`,
    `Visibility score: ${Number(lastResult.visibility_score || 0).toFixed(1)}/100`,
    lastResult.summary || "",
    "",
    "Missing signals:",
    ((lastResult.missing_signals && lastResult.missing_signals.keywords) || []).join(", ") || "None",
    "",
    "Fix now:",
    ...((lastResult.top_fixes || lastResult.recommendations || []).map((item) => `- ${item}`)),
    "",
    "What ATS sees:",
    ...((lastResult.what_ats_sees || []).map((item) => `- ${item}`)),
    "",
    "What recruiter sees:",
    ...((lastResult.what_recruiter_sees || []).map((item) => `- ${item}`)),
  ].join("\n");
}

resumeFile.addEventListener("change", updateFileLabels);
jdImage.addEventListener("change", updateFileLabels);
resumeFile.addEventListener("change", () => setStage("input"));
jdText.addEventListener("input", () => setStage("input"));
jdUrl.addEventListener("input", () => setStage("input"));

languageToggle.addEventListener("click", () => {
  setLanguage(currentLanguage === "en" ? "he" : "en");
  updateFileLabels();
  refreshRuntimeStatus();
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  gateError.textContent = "";
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ password: passwordInput.value }),
  });
  if (!response.ok) {
    gateError.textContent = currentLanguage === "he" ? "סיסמה לא נכונה." : "Incorrect password.";
    return;
  }
  passwordInput.value = "";
  await refreshAuth();
  setStatus(currentLanguage === "he" ? "הגישה אושרה" : "Access approved", currentLanguage === "he" ? "אפשר להריץ בדיקה." : "You can run the check now.", "idle");
});

logoutButton.addEventListener("click", async () => {
  await fetch(`${apiBaseUrl}/auth/logout`, { method: "POST", credentials: "same-origin" });
  await refreshAuth();
});

precheckButton.addEventListener("click", async () => {
  try {
    setStage("parse");
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
    setStage("match");
    setStatus("Analyzing ATS visibility", "Parsing, indexing, simulating recruiter search, and preparing fixes.", "loading");
    const payload = await postForm("/public/analyze");
    setStage(payload.ai_status === "completed" ? "rewrite" : "match");
    renderResult(payload);
    setStatus("Analysis complete", "Start with the decision, then fix the missing visibility signals.", "idle");
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
    document.getElementById("copyResult").textContent = t("copy");
  }, 1400);
});

downloadButton.addEventListener("click", () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ats_visibility_report.json";
  link.click();
  URL.revokeObjectURL(url);
});

setLanguage("en");
configureStaticMirror();
refreshAuth().catch(() => {
  authGate.classList.remove("hidden");
  analyzerSection.classList.add("locked");
});
