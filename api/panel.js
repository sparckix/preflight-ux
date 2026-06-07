const PROVIDERS = ["anthropic", "openai", "google"];

const SUPPORTED_MODELS = {
  anthropic: ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
  openai: ["gpt-5.5", "gpt-4.1", "gpt-4.1-mini", "o3", "o4-mini"],
  google: ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
};

const KEY_PATTERNS = {
  anthropic: /^sk-ant-[A-Za-z0-9_\-]{20,}$/,
  openai: /^sk-[A-Za-z0-9_\-]{20,}$/,
  google: /^[A-Za-z0-9_\-]{20,}$/
};

const IMAGE_DATA_URL = /^data:(image\/(?:png|jpeg|webp));base64,([A-Za-z0-9+/=]+)$/;

function validateByok(byok) {
  if (!byok || typeof byok !== "object") return "BYOK payload missing";
  const provider = String(byok.provider || "").toLowerCase();
  if (!PROVIDERS.includes(provider)) return "Unsupported provider";
  const key = String(byok.key || "").trim();
  if (!key) return "API key missing";
  if (key.length > 500) return "API key too long";
  if (!KEY_PATTERNS[provider].test(key)) return `API key shape does not match ${provider}'s expected format`;
  const model = String(byok.model || "");
  if (!SUPPORTED_MODELS[provider].includes(model)) return `Model not supported for ${provider}`;
  return null;
}

function normalizeImages(packet) {
  const screenshots = Array.isArray(packet?.attachments?.screenshots) ? packet.attachments.screenshots : [];
  return screenshots.slice(0, 3).flatMap((shot, index) => {
    const match = String(shot?.data_url || "").match(IMAGE_DATA_URL);
    if (!match) return [];
    return [{
      name: String(shot?.name || `screenshot-${index + 1}`).slice(0, 120),
      mimeType: match[1],
      base64: match[2]
    }];
  });
}

function buildPrompts(packet) {
  const personas = (packet?.panel?.personas || []).slice(0, 12).join(", ");
  const riskFocus = (packet?.panel?.risk_focus || []).join(", ");
  const product = packet?.product || {};
  const surface = String(product.surface || "").slice(0, 16000);
  const prototypeUrl = String(product.prototype_url || "").slice(0, 2000);
  const images = normalizeImages(packet);
  const imageList = images.map((image, index) => `${index + 1}. ${image.name} (${image.mimeType})`).join("\n") || "None";
  const review = packet?.review || {};
  const depthInstruction = review.depth === "deep"
    ? "Run a deep pass: inspect hierarchy, copy, trust, accessibility, repeat-use workflow, and likely edge cases."
    : "Run a fast pass: focus on the highest-confidence, lowest-regret issues.";
  const modeInstruction = {
    prioritized: "Prioritize risks by launch impact and fix leverage.",
    disagreement: "Emphasize where personas would disagree and what that implies for product decisions.",
    adversarial: "Actively search for brittle assumptions, trust failures, and ways the flow could be misread."
  }[review.synthesis_mode] || "Prioritize risks by launch impact and fix leverage.";
  const system = `You are Preflight UX, a pre-ship UX risk review system. You generate product-risk hypotheses, not real user research. Be concrete, conservative, and issue-class oriented. Return Markdown only.`;
  const user = `Review this product surface using the selected structured persona panel.\n\nProduct: ${product.name || "Untitled"}\nAudience: ${product.audience || "Unknown"}\nStage: ${product.stage || "Unknown"}\nSurface type: ${product.surface_type || "spec"}\nPrototype or live URL: ${prototypeUrl || "None provided"}\nPersonas: ${personas}\nRisk focus: ${riskFocus}\nReview depth: ${review.depth || "fast"}\nSynthesis mode: ${review.synthesis_mode || "prioritized"}\nAttached screenshots:\n${imageList}\n\nSurface notes:\n${surface}\n\n${depthInstruction} ${modeInstruction} Use screenshots as visual evidence when they are attached. Do not claim that you browsed the prototype URL unless the surface notes or screenshots provide evidence.\n\nFinding discipline:\n- Do not emit a risk without surface evidence.\n- Bind every risk to an issue class where possible.\n- Include a nearest confuser or alternative explanation so false positives can be audited.\n- Include a validation path and a stop or repair rule for each action card.\n- Return concise evidence and decisions; do not expose hidden chain-of-thought.\n\nReturn exactly these sections:\n1. Top risks table with Priority, Issue class, Sources, Evidence, Recommended change\n2. Action cards, each with Source, Severity, Confidence, Surface evidence, Predicted failure, Nearest confuser, Recommended change, Validation path, Stop or repair rule\n3. Persona disagreements\n4. Low-regret fixes to ship now\n5. What needs real-user validation\n6. Likely misses of this panel`;
  return { system, user, images };
}

function anthropicContent(prompts) {
  return [
    { type: "text", text: prompts.user },
    ...prompts.images.map((image) => ({
      type: "image",
      source: { type: "base64", media_type: image.mimeType, data: image.base64 }
    }))
  ];
}

function openAIContent(prompts) {
  return [
    { type: "text", text: prompts.user },
    ...prompts.images.map((image) => ({
      type: "image_url",
      image_url: { url: `data:${image.mimeType};base64,${image.base64}` }
    }))
  ];
}

function googleParts(prompts) {
  return [
    { text: prompts.user },
    ...prompts.images.map((image) => ({
      inlineData: { mimeType: image.mimeType, data: image.base64 }
    }))
  ];
}

async function callAnthropic(byok, prompts) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": byok.key,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: byok.model,
      max_tokens: 2400,
      temperature: 0.2,
      system: prompts.system,
      messages: [{ role: "user", content: anthropicContent(prompts) }]
    })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data?.error?.message || `Anthropic error ${response.status}`);
  return (data.content || []).filter((block) => block.type === "text").map((block) => block.text).join("");
}

async function callOpenAI(byok, prompts) {
  const isReasoning = /^(o\d|gpt-5\.5)/i.test(byok.model);
  const body = {
    model: byok.model,
    messages: [
      { role: "system", content: prompts.system },
      { role: "user", content: openAIContent(prompts) }
    ],
    max_completion_tokens: isReasoning ? 6000 : 2400
  };
  if (!isReasoning) body.temperature = 0.2;
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${byok.key}`
    },
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data?.error?.message || `OpenAI error ${response.status}`);
  return data.choices?.[0]?.message?.content || "";
}

async function callGoogle(byok, prompts) {
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(byok.model)}:generateContent?key=${encodeURIComponent(byok.key)}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: prompts.system }] },
      contents: [{ role: "user", parts: googleParts(prompts) }],
      generationConfig: { temperature: 0.2, maxOutputTokens: 2400 }
    })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data?.error?.message || `Google error ${response.status}`);
  return data.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("") || "";
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { byok, packet } = req.body || {};
    const validationError = validateByok(byok);
    if (validationError) return res.status(400).json({ error: validationError });

    const prompts = buildPrompts(packet);
    let markdown = "";
    if (byok.provider === "anthropic") markdown = await callAnthropic(byok, prompts);
    if (byok.provider === "openai") markdown = await callOpenAI(byok, prompts);
    if (byok.provider === "google") markdown = await callGoogle(byok, prompts);

    return res.status(200).json({ markdown, provider: byok.provider, model: byok.model, image_count: prompts.images.length, prompt_version: packet?.prompt_version || "web-byok-v0.4" });
  } catch (error) {
    return res.status(500).json({ error: error?.message || "Panel run failed" });
  }
};
