const STORAGE_KEY = "preflight-ux.byok.v1";
const HISTORY_KEY = "preflight-ux.history.v1";
const MAX_SCREENSHOTS = 3;
const MAX_SCREENSHOT_BYTES = 1800000;
const PROMPT_VERSION = "web-byok-v0.4";

const supportedModels = {
  anthropic: ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
  openai: ["gpt-5.5", "gpt-4.1", "gpt-4.1-mini", "o3", "o4-mini"],
  google: ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
};

const personas = [
  { id: "maya-editorial-designer", type: "UX expert", note: "Typography, rhythm, register" },
  { id: "daniel-k-operator-tool", type: "UX expert", note: "Density, shortcuts, repeat use" },
  { id: "sara-ux-researcher", type: "UX expert", note: "Mental models, framing, agency" },
  { id: "jamie-accessibility", type: "UX expert", note: "Contrast, semantics, focus, live regions" },
  { id: "rio-growth-brand", type: "UX expert", note: "Shareability, brand, first impression" },
  { id: "priya-mba-deadline", type: "User type", note: "Deadline-driven first-use speed" },
  { id: "marcus-junior-consultant", type: "User type", note: "Credibility, output sharing, speed" },
  { id: "elena-founder-skeptical", type: "User type", note: "Technical trust, no fluff, export" },
  { id: "greg-pe-partner", type: "User type", note: "Low patience, high trust threshold" },
  { id: "aisha-policy-researcher", type: "User type", note: "Domain mismatch and coverage honesty" },
  { id: "yuki-ai-researcher", type: "User type", note: "Adversarial tests and provenance" },
  { id: "tom-random-visitor", type: "User type", note: "No context, fast value test" }
];

const risks = [
  ["empty-state-confusion", "First-use clarity and example output"],
  ["loading-abandonment", "Wait states, progress, retry risk"],
  ["copy-anchoring-on-verdict", "Framing, ego load, verdict copy"],
  ["accessibility-focus-management", "Keyboard, focus, dynamic output"],
  ["trust-without-provenance", "Evidence, confidence, source quality"],
  ["screenshot-export-friction", "Share, export, downstream use"],
  ["domain-mismatch-trust-break", "Audience/domain credibility"],
  ["navigation-discoverability", "Wayfinding and hidden actions"]
];

const sampleSurface = `Product: Preflight UX web UI\nAudience: product builders using LLMs for pre-ship critique\nSurface: single-page web app with a product brief form, persona checklist, risk focus controls, BYOK model settings, uploaded screenshots, and generated review brief.\nPrimary task: paste a product surface, add screenshots or a prototype URL, select personas, generate or run a structured panel review.\nConstraints: deployable to Vercel, BYOK only, no persistent server-side storage.\nKnown concern: users may not understand which artifacts are sent to the provider.`;

function el(id) { return document.getElementById(id); }

function loadByok() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { enabled: false, provider: "anthropic", model: "claude-sonnet-4-6", key: "" };
    const parsed = JSON.parse(raw);
    const provider = supportedModels[parsed.provider] ? parsed.provider : "anthropic";
    return {
      enabled: Boolean(parsed.enabled),
      provider,
      model: supportedModels[provider].includes(parsed.model) ? parsed.model : supportedModels[provider][0],
      key: typeof parsed.key === "string" ? parsed.key : ""
    };
  } catch {
    return { enabled: false, provider: "anthropic", model: "claude-sonnet-4-6", key: "" };
  }
}

let byok = loadByok();
let lastPanelMarkdown = "";
let lastRunMeta = null;
let normalizedFindings = [];
let screenshotAttachments = [];

function saveByok() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(byok));
  updateByokUI();
}

function loadHistory() {
  try {
    const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveHistory(items) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 8)));
  renderHistory();
}

function sanitizeBriefForHistory(brief) {
  return {
    ...brief,
    attachments: {
      screenshots: (brief.attachments?.screenshots || []).map((shot) => ({
        name: shot.name,
        mime_type: shot.mime_type,
        size_bytes: shot.size_bytes
      }))
    }
  };
}

function addHistoryEntry(kind) {
  const brief = buildPacket();
  const entry = {
    id: `${brief.run_id}-${Date.now()}`,
    kind,
    run_id: brief.run_id,
    product_name: brief.product.name,
    created_at: new Date().toISOString(),
    provider: lastRunMeta?.provider || byok.provider,
    model: lastRunMeta?.model || byok.model,
    image_count: screenshotAttachments.length,
    brief: sanitizeBriefForHistory(brief),
    markdown: lastPanelMarkdown,
    findings: normalizedFindings
  };
  saveHistory([entry, ...loadHistory().filter((item) => item.id !== entry.id)]);
}

function renderHistory() {
  const items = loadHistory();
  const target = el("historyList");
  if (!items.length) {
    target.innerHTML = '<p class="muted">No local runs saved yet.</p>';
    return;
  }
  target.innerHTML = items.map((item) => `
    <article class="history-item">
      <div>
        <strong>${escapeHtml(item.product_name || item.run_id)}</strong>
        <span>${escapeHtml(item.kind)} · ${escapeHtml(item.model || "unrun")} · ${new Date(item.created_at).toLocaleString()}</span>
      </div>
      <button class="ghost" type="button" data-history-id="${item.id}">Restore</button>
    </article>
  `).join("");
  target.querySelectorAll("button[data-history-id]").forEach((button) => {
    button.addEventListener("click", () => restoreHistoryEntry(button.getAttribute("data-history-id")));
  });
}

function restoreHistoryEntry(id) {
  const item = loadHistory().find((entry) => entry.id === id);
  if (!item) return;
  applyBrief(item.brief, { restoreScreenshots: false });
  lastPanelMarkdown = item.markdown || "";
  normalizedFindings = Array.isArray(item.findings) ? item.findings : [];
  renderFindingsEditor();
  lastRunMeta = {
    provider: item.provider,
    model: item.model,
    image_count: item.image_count || 0,
    prompt_version: PROMPT_VERSION,
    timestamp: item.created_at
  };
  if (lastPanelMarkdown) setPanelMarkdown(lastPanelMarkdown);
  renderProvenance();
  setValidationMessages(validateReviewBrief(buildPacket()));
}

function renderRiskFocus() {
  el("riskFocus").innerHTML = risks.map(([id, note], index) => `
    <label class="check-item">
      <input type="checkbox" value="${id}" ${index < 5 ? "checked" : ""} />
      <span>${id}<small>${note}</small></span>
    </label>
  `).join("");
}

function renderPersonas() {
  el("personaList").innerHTML = personas.map((persona) => `
    <label class="persona-item">
      <input type="checkbox" value="${persona.id}" checked />
      <span>${persona.id}<small>${persona.type}: ${persona.note}</small></span>
    </label>
  `).join("");
}

function renderModels() {
  el("byokModel").innerHTML = supportedModels[byok.provider]
    .map((model) => `<option value="${model}">${model}</option>`)
    .join("");
  el("byokModel").value = byok.model;
}

function updateByokUI() {
  el("byokEnabled").checked = byok.enabled;
  el("byokProvider").value = byok.provider;
  renderModels();
  el("byokKey").value = byok.key;
  el("byokFields").classList.toggle("active", byok.enabled);
  el("byokStatus").textContent = byok.enabled && byok.key ? `${byok.provider} · ${byok.model}` : "BYOK off";
}

function selectedValues(selector) {
  return Array.from(document.querySelectorAll(selector))
    .filter((input) => input.checked)
    .map((input) => input.value);
}

function setCheckedValues(selector, values) {
  const wanted = new Set(values || []);
  document.querySelectorAll(selector).forEach((input) => { input.checked = wanted.has(input.value); });
}

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "product";
}

function buildPacket() {
  const productName = el("productName").value.trim() || "Untitled product";
  const runId = `${slugify(productName)}-${new Date().toISOString().slice(0, 10)}`;
  return {
    artifact_type: "preflight_ux_review_brief",
    schema_version: "0.3",
    run_id: runId,
    prompt_version: PROMPT_VERSION,
    product: {
      name: productName,
      audience: el("audience").value.trim(),
      stage: el("stage").value,
      surface_type: el("surfaceType").value,
      prototype_url: el("prototypeUrl").value.trim(),
      surface: el("surface").value.trim()
    },
    attachments: {
      screenshots: screenshotAttachments.map((item) => ({
        name: item.name,
        mime_type: item.mimeType,
        size_bytes: item.size,
        data_url: item.dataUrl
      }))
    },
    review: {
      depth: el("reviewDepth").value,
      synthesis_mode: el("synthesisMode").value
    },
    panel: {
      personas: selectedValues('#personaList input[type="checkbox"]'),
      risk_focus: selectedValues('#riskFocus input[type="checkbox"]')
    },
    workflow: [
      "Run each selected persona independently or run the synthesized BYOK panel.",
      "Use uploaded screenshots as visual evidence, not as proof of real user behavior.",
      "Normalize findings to taxonomy slugs.",
      "Synthesize a prioritized product report.",
      "Validate important claims with real users or telemetry."
    ],
    cli_next_steps: [
      `uxpanel validate-artifact --type review-brief ${runId}-review-brief.json`,
      `uxpanel run --surface surfaces/${runId}.md --run-id ${runId}`,
      `uxpanel report --run runs/${runId}`
    ]
  };
}

function validateReviewBrief(brief) {
  const errors = [];
  const warnings = [];
  if (brief.artifact_type !== "preflight_ux_review_brief") errors.push("Artifact type must be preflight_ux_review_brief.");
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(brief.run_id || "")) errors.push("Run id must be a lowercase slug.");
  if (!brief.product?.name?.trim()) errors.push("Product name is required.");
  const hasSurface = Boolean(brief.product?.surface?.trim());
  const hasUrl = Boolean(brief.product?.prototype_url?.trim());
  const screenshots = brief.attachments?.screenshots || [];
  if (!hasSurface && !hasUrl && screenshots.length === 0) errors.push("Add surface notes, a prototype URL, or at least one screenshot.");
  if (hasUrl && screenshots.length === 0) warnings.push("Prototype URLs are not browsed automatically yet. Add screenshots for visual review.");
  if (!brief.panel?.personas?.length) errors.push("Select at least one persona.");
  if (!brief.panel?.risk_focus?.length) errors.push("Select at least one risk focus.");
  if (screenshots.length > MAX_SCREENSHOTS) errors.push(`Attach at most ${MAX_SCREENSHOTS} screenshots.`);
  screenshots.forEach((shot) => {
    if (!/^image\/(png|jpeg|webp)$/.test(shot.mime_type || "")) errors.push(`${shot.name || "Screenshot"} must be PNG, JPG, or WebP.`);
    if ((shot.size_bytes || 0) > MAX_SCREENSHOT_BYTES) errors.push(`${shot.name || "Screenshot"} is over 1.8 MB.`);
  });
  return { errors, warnings };
}

function setValidationMessages(result) {
  const box = el("validationBox");
  const messages = [...result.errors.map((item) => ["error", item]), ...result.warnings.map((item) => ["warning", item])];
  if (!messages.length) {
    box.className = "validation-box ok";
    box.textContent = "Review brief is valid for a BYOK run.";
    return true;
  }
  box.className = `validation-box ${result.errors.length ? "error" : "warning"}`;
  box.innerHTML = messages.map(([kind, item]) => `<div><strong>${kind}</strong> ${escapeHtml(item)}</div>`).join("");
  return result.errors.length === 0;
}


function issueSlug(value) {
  const match = String(value || "").toLowerCase().match(/[a-z0-9]+(?:-[a-z0-9]+)+/);
  return match ? match[0] : slugify(String(value || "issue"));
}

function firstPersona(value) {
  const known = personas.map((persona) => persona.id);
  const text = String(value || "").toLowerCase();
  return known.find((id) => text.includes(id)) || known.find((id) => text.includes(id.split("-")[0])) || selectedValues('#personaList input[type="checkbox"]')[0] || "tom-random-visitor";
}

function severityFromPriority(value) {
  const priority = String(value || "").toUpperCase();
  if (priority.includes("P0")) return "severe";
  if (priority.includes("P1")) return "moderate";
  return "minor";
}

function splitMarkdownRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function parseFindingsFromMarkdown(markdown) {
  const rows = String(markdown || "").split("\n")
    .filter((line) => /^\s*\|/.test(line))
    .map(splitMarkdownRow)
    .filter((cells) => cells.length >= 5)
    .filter((cells) => !cells.join(" ").toLowerCase().includes("issue class"))
    .filter((cells) => !cells.every((cell) => /^:?-{3,}:?$/.test(cell)));
  return rows.map((cells, index) => {
    const hasSeverityColumns = cells.length >= 6 && ["minor", "moderate", "severe"].includes(cells[3].toLowerCase());
    const priority = cells[0];
    const issueClass = issueSlug(cells[1]);
    const persona = firstPersona(cells[2]);
    const severity = hasSeverityColumns ? cells[3].toLowerCase() : severityFromPriority(priority);
    const confidence = hasSeverityColumns && ["low", "medium", "high"].includes(cells[4].toLowerCase()) ? cells[4].toLowerCase() : "medium";
    const evidence = hasSeverityColumns ? "" : cells[3];
    const recommendation = hasSeverityColumns ? cells[5] : cells[4];
    return {
      id: `finding-${String(index + 1).padStart(3, "0")}`,
      persona,
      raw_finding: evidence || recommendation || `Potential ${issueClass} risk.`,
      issue_class: issueClass,
      severity,
      confidence,
      evidence,
      recommendation
    };
  });
}

function emptyFinding() {
  return {
    id: `finding-${String(normalizedFindings.length + 1).padStart(3, "0")}`,
    persona: selectedValues('#personaList input[type="checkbox"]')[0] || "tom-random-visitor",
    raw_finding: "",
    issue_class: selectedValues('#riskFocus input[type="checkbox"]')[0] || "empty-state-confusion",
    severity: "moderate",
    confidence: "medium",
    evidence: "",
    recommendation: ""
  };
}

function renderFindingsEditor() {
  const target = el("findingsList");
  el("downloadRunJson").disabled = normalizedFindings.length === 0;
  if (!normalizedFindings.length) {
    target.innerHTML = '<p class="muted">No normalized findings yet. Run the panel, parse Markdown, or add a finding manually.</p>';
    return;
  }
  target.innerHTML = normalizedFindings.map((finding, index) => `
    <article class="finding-card" data-index="${index}">
      <div class="finding-card-head">
        <strong>${escapeHtml(finding.id)}</strong>
        <button class="ghost" type="button" data-action="remove-finding" data-index="${index}">Remove</button>
      </div>
      <div class="finding-grid">
        <label>Issue class<input data-field="issue_class" data-index="${index}" value="${escapeHtml(finding.issue_class)}" /></label>
        <label>Persona<input data-field="persona" data-index="${index}" value="${escapeHtml(finding.persona)}" /></label>
        <label>Severity<select data-field="severity" data-index="${index}">
          ${["minor", "moderate", "severe"].map((item) => `<option ${finding.severity === item ? "selected" : ""}>${item}</option>`).join("")}
        </select></label>
        <label>Confidence<select data-field="confidence" data-index="${index}">
          ${["low", "medium", "high"].map((item) => `<option ${finding.confidence === item ? "selected" : ""}>${item}</option>`).join("")}
        </select></label>
      </div>
      <label>Predicted behavior<textarea data-field="raw_finding" data-index="${index}" rows="2">${escapeHtml(finding.raw_finding)}</textarea></label>
      <label>Evidence<textarea data-field="evidence" data-index="${index}" rows="2">${escapeHtml(finding.evidence || "")}</textarea></label>
      <label>Recommendation<textarea data-field="recommendation" data-index="${index}" rows="2">${escapeHtml(finding.recommendation || "")}</textarea></label>
    </article>
  `).join("");
}

function updateFinding(event) {
  const index = Number(event.target?.dataset?.index);
  const field = event.target?.dataset?.field;
  if (!Number.isInteger(index) || !field || !normalizedFindings[index]) return;
  normalizedFindings[index][field] = event.target.value;
}

function removeFinding(index) {
  normalizedFindings.splice(index, 1);
  normalizedFindings = normalizedFindings.map((finding, nextIndex) => ({ ...finding, id: `finding-${String(nextIndex + 1).padStart(3, "0")}` }));
  renderFindingsEditor();
}

function buildPanelRunJson() {
  const packet = buildPacket();
  const ref = packet.product.prototype_url || `web-review-brief:${packet.run_id}`;
  return {
    run_id: packet.run_id,
    surface: { type: packet.product.surface_type, ref, hash: "" },
    model: {
      provider: lastRunMeta?.provider || byok.provider || "manual",
      name: lastRunMeta?.model || byok.model || "unrun",
      version: lastRunMeta?.prompt_version || PROMPT_VERSION,
      temperature: 0.2
    },
    prompt_version: lastRunMeta?.prompt_version || PROMPT_VERSION,
    date: (lastRunMeta?.timestamp || new Date().toISOString()).slice(0, 10),
    personas: packet.panel.personas,
    findings: normalizedFindings.map((finding) => ({
      id: issueSlug(finding.id),
      persona: firstPersona(finding.persona),
      raw_finding: finding.raw_finding || finding.evidence || finding.recommendation || "Unspecified finding.",
      issue_class: issueSlug(finding.issue_class),
      severity: ["minor", "moderate", "severe"].includes(finding.severity) ? finding.severity : "moderate",
      confidence: ["low", "medium", "high"].includes(finding.confidence) ? finding.confidence : "medium",
      evidence: finding.evidence || "",
      recommendation: finding.recommendation || ""
    }))
  };
}

function downloadRunJson() {
  const run = buildPanelRunJson();
  downloadBlob(`${run.run_id}.run.json`, JSON.stringify(run, null, 2) + "\n", "application/json");
  addHistoryEntry("run-json-export");
}

function renderPacket() {
  const packet = buildPacket();
  el("packetOutput").textContent = JSON.stringify(packet, null, 2);
  setValidationMessages(validateReviewBrief(packet));
}

function renderScreenshotPreview() {
  const count = screenshotAttachments.length;
  el("attachmentStatus").textContent = count ? `${count} screenshot${count === 1 ? "" : "s"} attached for visual review.` : "No screenshots added.";
  el("clearScreenshots").disabled = count === 0;
  el("screenshotPreview").innerHTML = screenshotAttachments.map((item, index) => `
    <figure class="screenshot-card">
      <img src="${item.dataUrl}" alt="Uploaded screenshot ${index + 1}: ${item.name}" />
      <figcaption>${escapeHtml(item.name)}<span>${Math.round(item.size / 1024)} KB</span></figcaption>
    </figure>
  `).join("");
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(new Error(`Could not read ${file.name}`));
    reader.readAsDataURL(file);
  });
}

async function handleScreenshots(event) {
  const files = Array.from(event.target.files || []);
  const slots = MAX_SCREENSHOTS - screenshotAttachments.length;
  const accepted = files
    .filter((file) => /^image\/(png|jpeg|webp)$/.test(file.type) && file.size <= MAX_SCREENSHOT_BYTES)
    .slice(0, Math.max(0, slots));
  for (const file of accepted) {
    const dataUrl = await readFileAsDataUrl(file);
    screenshotAttachments.push({ name: file.name, mimeType: file.type, size: file.size, dataUrl });
  }
  const skipped = files.length - accepted.length;
  renderScreenshotPreview();
  renderPacket();
  if (skipped > 0) {
    el("attachmentStatus").textContent += ` ${skipped} file${skipped === 1 ? "" : "s"} skipped; use PNG, JPG, or WebP under 1.8 MB, max ${MAX_SCREENSHOTS}.`;
  }
  event.target.value = "";
}

function clearScreenshots() {
  screenshotAttachments = [];
  renderScreenshotPreview();
  renderPacket();
}

function downloadBlob(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function downloadPacket() {
  const packet = buildPacket();
  downloadBlob(`${packet.run_id}-review-brief.json`, JSON.stringify(packet, null, 2) + "\n", "application/json");
  addHistoryEntry("brief-export");
}

function provenanceLines() {
  const packet = buildPacket();
  const meta = lastRunMeta || {};
  return [
    `Run id: ${packet.run_id}`,
    `Generated: ${meta.timestamp || new Date().toISOString()}`,
    `Provider/model: ${meta.provider || byok.provider}/${meta.model || byok.model}`,
    `Prompt version: ${meta.prompt_version || PROMPT_VERSION}`,
    `Review depth: ${packet.review.depth}`,
    `Synthesis mode: ${packet.review.synthesis_mode}`,
    `Personas: ${packet.panel.personas.join(", ") || "none"}`,
    `Risk focus: ${packet.panel.risk_focus.join(", ") || "none"}`,
    `Screenshots: ${meta.image_count ?? packet.attachments.screenshots.length}`,
    `Prototype/live URL: ${packet.product.prototype_url || "none"}`
  ];
}

function structuredFindingsMarkdown() {
  if (!normalizedFindings.length) return "No normalized findings recorded yet.";
  return normalizedFindings.map((finding) => `### ${finding.id}: \`${finding.issue_class}\`\n\n- Persona: \`${finding.persona}\`\n- Severity: \`${finding.severity}\`\n- Confidence: \`${finding.confidence}\`\n- Predicted behavior: ${finding.raw_finding || ""}\n- Evidence: ${finding.evidence || ""}\n- Recommendation: ${finding.recommendation || ""}`).join("\n\n");
}

function buildReportMarkdown() {
  const packet = buildPacket();
  const panel = lastPanelMarkdown.trim() || "No panel output recorded yet.";
  return `# Preflight UX Report: ${packet.product.name}\n\n## Provenance\n\n${provenanceLines().map((line) => `- ${line}`).join("\n")}\n\n## Product Surface\n\n- Audience: ${packet.product.audience || "Unknown"}\n- Stage: ${packet.product.stage}\n- Surface type: ${packet.product.surface_type}\n\n${packet.product.surface || "No written surface notes provided."}\n\n## Structured Findings\n\n${structuredFindingsMarkdown()}\n\n## Raw Panel Output\n\n${panel}\n\n## Validation Notes\n\n- Treat these findings as pre-ship hypotheses, not validated user research.\n- Validate high-severity findings with real users, telemetry, support data, or launch retrospectives.\n- Prototype URLs are included as references; screenshots are the visual evidence supplied to the model.\n`;
}

function downloadResultMarkdown() {
  if (!lastPanelMarkdown.trim()) return;
  const packet = buildPacket();
  const content = `# Raw Preflight UX Panel Output\n\n## Provenance\n\n${provenanceLines().map((line) => `- ${line}`).join("\n")}\n\n## Output\n\n${lastPanelMarkdown.trim()}\n`;
  downloadBlob(`${packet.run_id}-panel.md`, content, "text/markdown");
}

function downloadReportMarkdown() {
  const packet = buildPacket();
  downloadBlob(`${packet.run_id}-report.md`, buildReportMarkdown(), "text/markdown");
  addHistoryEntry("report-export");
}

function renderProvenance() {
  const box = el("provenanceBox");
  if (!lastRunMeta) {
    box.innerHTML = "";
    return;
  }
  box.innerHTML = `<h3>Run provenance</h3><ul>${provenanceLines().map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul>`;
}

function setPanelText(message, isError = false) {
  const result = el("panelResult");
  result.setAttribute("role", isError ? "alert" : "status");
  result.textContent = message;
}

function setPanelMarkdown(markdown) {
  lastPanelMarkdown = markdown || "";
  const result = el("panelResult");
  result.setAttribute("role", "status");
  result.innerHTML = markdownToHtml(lastPanelMarkdown || "No output returned.");
  const parsed = parseFindingsFromMarkdown(lastPanelMarkdown);
  if (parsed.length) normalizedFindings = parsed;
  renderFindingsEditor();
  el("downloadResult").disabled = !lastPanelMarkdown.trim();
  el("downloadReport").disabled = false;
}

function setRunningState(isRunning) {
  el("output").setAttribute("aria-busy", isRunning ? "true" : "false");
  el("runPanel").disabled = isRunning;
  el("runPanel").textContent = isRunning ? "Running" : "Run panel";
}

async function copyPacket() {
  if (!el("packetOutput").textContent.trim()) renderPacket();
  await navigator.clipboard.writeText(el("packetOutput").textContent);
  el("copyPacket").textContent = "Copied";
  window.setTimeout(() => { el("copyPacket").textContent = "Copy"; }, 1200);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function markdownToHtml(markdown) {
  const escaped = escapeHtml(markdown);
  return escaped
    .replace(/^### (.*)$/gm, "<h3>$1</h3>")
    .replace(/^## (.*)$/gm, "<h2>$1</h2>")
    .replace(/^# (.*)$/gm, "<h1>$1</h1>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/^/, "<p>")
    .replace(/$/, "</p>");
}

async function runPanel() {
  renderPacket();
  lastPanelMarkdown = "";
  lastRunMeta = null;
  el("downloadResult").disabled = true;
  el("downloadReport").disabled = true;
  const brief = buildPacket();
  const validation = validateReviewBrief(brief);
  if (!setValidationMessages(validation)) {
    setPanelText("Fix review brief validation errors before running the panel.", true);
    return;
  }
  if (!byok.enabled || !byok.key.trim()) {
    setPanelText("Enable BYOK and add an API key before running the panel.", true);
    return;
  }
  setRunningState(true);
  setPanelText("Running panel through /api/panel with your selected provider...");
  try {
    const response = await fetch("/api/panel", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        byok: { provider: byok.provider, model: byok.model, key: byok.key.trim() },
        packet: brief
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Panel run failed");
    lastRunMeta = {
      provider: data.provider || byok.provider,
      model: data.model || byok.model,
      image_count: data.image_count ?? brief.attachments.screenshots.length,
      prompt_version: data.prompt_version || PROMPT_VERSION,
      timestamp: new Date().toISOString()
    };
    renderProvenance();
    setPanelMarkdown(data.markdown || "No output returned.");
    addHistoryEntry("panel-run");
  } catch (error) {
    setPanelText(error.message || "Panel run failed.", true);
  } finally {
    setRunningState(false);
  }
}

function applyBrief(brief, options = { restoreScreenshots: true }) {
  el("productName").value = brief.product?.name || brief.run_id || "Untitled product";
  el("audience").value = brief.product?.audience || "";
  el("stage").value = brief.product?.stage || "pre-ship";
  el("surfaceType").value = brief.product?.surface_type || "spec";
  el("prototypeUrl").value = brief.product?.prototype_url || "";
  el("surface").value = brief.product?.surface || "";
  el("reviewDepth").value = brief.review?.depth || "fast";
  el("synthesisMode").value = brief.review?.synthesis_mode || "prioritized";
  setCheckedValues('#personaList input[type="checkbox"]', brief.panel?.personas || []);
  setCheckedValues('#riskFocus input[type="checkbox"]', brief.panel?.risk_focus || []);
  if (options.restoreScreenshots) {
    screenshotAttachments = (brief.attachments?.screenshots || []).filter((shot) => shot.data_url).map((shot) => ({
      name: shot.name || "screenshot",
      mimeType: shot.mime_type || "image/png",
      size: shot.size_bytes || 0,
      dataUrl: shot.data_url
    }));
  } else {
    screenshotAttachments = [];
  }
  renderScreenshotPreview();
  renderPacket();
}

function runToBrief(run) {
  return {
    artifact_type: "preflight_ux_review_brief",
    schema_version: "0.3",
    run_id: run.run_id || "imported-run",
    prompt_version: run.prompt_version || PROMPT_VERSION,
    product: {
      name: run.run_id || "Imported run",
      audience: "",
      stage: "post-launch",
      surface_type: run.surface?.type || "spec",
      prototype_url: run.surface?.type === "url" || run.surface?.type === "prototype" ? run.surface?.ref || "" : "",
      surface: run.surface?.ref ? `Imported from run surface: ${run.surface.ref}` : ""
    },
    attachments: { screenshots: [] },
    review: { depth: "fast", synthesis_mode: "prioritized" },
    panel: { personas: run.personas || [], risk_focus: Array.from(new Set((run.findings || []).map((finding) => finding.issue_class).filter(Boolean))) }
  };
}

async function importJson(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    const parsed = JSON.parse(await file.text());
    if (parsed.artifact_type === "preflight_ux_review_brief") {
      applyBrief(parsed, { restoreScreenshots: true });
      setPanelText(`Imported review brief: ${parsed.run_id}`);
    } else if (parsed.run_id && parsed.surface && parsed.personas) {
      applyBrief(runToBrief(parsed), { restoreScreenshots: false });
      normalizedFindings = Array.isArray(parsed.findings) ? parsed.findings : [];
      lastRunMeta = { provider: parsed.model?.provider || "manual", model: parsed.model?.name || "imported", prompt_version: parsed.prompt_version || PROMPT_VERSION, timestamp: parsed.date || new Date().toISOString(), image_count: 0 };
      renderFindingsEditor();
      renderProvenance();
      setPanelText(`Imported run.json as an editable review brief: ${parsed.run_id}`);
    } else {
      throw new Error("JSON is not a Preflight UX review brief or panel run.");
    }
  } catch (error) {
    setPanelText(error.message || "Import failed.", true);
  } finally {
    event.target.value = "";
  }
}

renderRiskFocus();
renderPersonas();
updateByokUI();
renderScreenshotPreview();
renderPacket();
renderFindingsEditor();
renderHistory();

el("generatePacket").addEventListener("click", () => { renderPacket(); addHistoryEntry("brief-build"); });
el("validateBrief").addEventListener("click", () => setValidationMessages(validateReviewBrief(buildPacket())));
el("downloadPacket").addEventListener("click", downloadPacket);
el("downloadResult").addEventListener("click", downloadResultMarkdown);
el("downloadReport").addEventListener("click", downloadReportMarkdown);
el("downloadRunJson").addEventListener("click", downloadRunJson);
el("parseFindings").addEventListener("click", () => { normalizedFindings = parseFindingsFromMarkdown(lastPanelMarkdown); renderFindingsEditor(); });
el("addFinding").addEventListener("click", () => { normalizedFindings.push(emptyFinding()); renderFindingsEditor(); });
el("findingsList").addEventListener("input", updateFinding);
el("findingsList").addEventListener("change", updateFinding);
el("findingsList").addEventListener("click", (event) => { if (event.target?.dataset?.action === "remove-finding") removeFinding(Number(event.target.dataset.index)); });
el("copyPacket").addEventListener("click", copyPacket);
el("runPanel").addEventListener("click", runPanel);
el("screenshotInput").addEventListener("change", handleScreenshots);
el("importInput").addEventListener("change", importJson);
el("clearScreenshots").addEventListener("click", clearScreenshots);
el("clearHistory").addEventListener("click", () => saveHistory([]));
el("selectDefault").addEventListener("click", () => {
  document.querySelectorAll('#personaList input[type="checkbox"]').forEach((input) => { input.checked = true; });
  renderPacket();
});
el("loadSample").addEventListener("click", () => {
  el("productName").value = "Preflight UX web UI";
  el("audience").value = "Product builders and design reviewers";
  el("stage").value = "prototype";
  el("surfaceType").value = "prototype";
  el("prototypeUrl").value = "https://preflight-ux.vercel.app";
  el("surface").value = sampleSurface;
  el("reviewDepth").value = "deep";
  el("synthesisMode").value = "disagreement";
  renderPacket();
});
el("byokEnabled").addEventListener("change", (event) => { byok.enabled = event.target.checked; saveByok(); });
el("byokProvider").addEventListener("change", (event) => {
  byok.provider = event.target.value;
  byok.model = supportedModels[byok.provider][0];
  saveByok();
});
el("byokModel").addEventListener("change", (event) => { byok.model = event.target.value; saveByok(); });
el("byokKey").addEventListener("input", (event) => { byok.key = event.target.value; saveByok(); });
el("toggleKey").addEventListener("click", () => {
  const input = el("byokKey");
  input.type = input.type === "password" ? "text" : "password";
  el("toggleKey").textContent = input.type === "password" ? "Show" : "Hide";
});
el("clearKey").addEventListener("click", () => {
  byok = { enabled: false, provider: "anthropic", model: "claude-sonnet-4-6", key: "" };
  localStorage.removeItem(STORAGE_KEY);
  updateByokUI();
});

document.querySelectorAll("input, select, textarea").forEach((node) => {
  node.addEventListener("change", renderPacket);
});
el("surface").addEventListener("input", renderPacket);
el("prototypeUrl").addEventListener("input", renderPacket);
