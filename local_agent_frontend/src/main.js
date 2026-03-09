import "./style.css";
import { marked } from "marked";

function createThreadId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }

  const random = Math.random().toString(36).slice(2, 10);
  return `thread-${Date.now()}-${random}`;
}

const defaultThreadId = createThreadId();

const state = {
  apiBase: localStorage.getItem("agent-api-base") || "/api/v1",
  threadId: localStorage.getItem("agent-thread-id") || defaultThreadId,
  messages: [],
  latestRetrievalMetrics: null,
  latestCompareReport: null,
  latestBenchmarkMetrics: null,
  activeTrace: [],
  statusTimer: null,
  requestStartedAt: null,
  railOpen: false,
  activeEvalAction: "runRetrievalEval",
  streamingAnswer: "",
};

marked.setOptions({
  gfm: true,
  breaks: true,
});

const app = document.querySelector("#app");

app.innerHTML = `
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark">IA</div>
        <div>
          <p class="eyebrow">Policy And Tender Agent</p>
          <h1>InsightAgent</h1>
        </div>
        <button id="closeRail" class="ghost rail-close">关闭</button>
      </div>

      <div class="stack">
        <label class="field">
          <span>API Base</span>
          <input id="apiBase" value="${state.apiBase}" placeholder="/api/v1" />
        </label>
        <label class="field">
          <span>Thread ID</span>
          <div class="inline">
            <input id="threadId" value="${state.threadId}" />
            <button id="regenThread" class="ghost">重置</button>
          </div>
        </label>
        <label class="field">
          <span>User ID</span>
          <input id="userId" placeholder="例如：liushiji" />
        </label>
      </div>

      <div class="mini-metrics compact-metrics">
        <div class="mini-card">
          <span>Chat Mode</span>
          <strong>ReAct + Planner</strong>
        </div>
        <div class="mini-card">
          <span>Retrieval</span>
          <strong>Hybrid + Rerank</strong>
        </div>
      </div>

      <section class="panel compact-panel">
        <div class="panel-head tight">
          <div>
            <p class="eyebrow">Knowledge</p>
            <h3>知识库上传</h3>
          </div>
        </div>
        <div class="stack">
          <input id="knowledgeFile" type="file" />
          <button id="uploadKnowledge">上传并入库</button>
          <pre id="uploadResult" class="result-box compact-result"></pre>
        </div>
      </section>
    </aside>

    <main class="workspace">
      <div class="mobile-toolbar">
        <button id="openRail" class="ghost">菜单</button>
      </div>
      <header class="workspace-header">
        <div>
          <p class="eyebrow">Agent Console</p>
          <h2>InsightAgent</h2>
          <p class="hero-text">面向政策通知、招投标公告与本地知识资料分析的多模式 Agent 工作台。</p>
        </div>
      </header>

      <section class="panel chat-panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Chat</p>
            <h3>对话工作区</h3>
          </div>
          <div class="inline compact">
            <button id="clearChat" class="ghost">清空会话</button>
          </div>
        </div>

        <div class="chat-stack">
          <section class="response-card chat-history-card">
            <div class="response-head">
              <p class="eyebrow">Conversation</p>
              <strong>当前回答与历史记录</strong>
            </div>
            <div id="messageList" class="message-list"></div>
          </section>

          <section class="response-card trace-card">
            <div class="response-head">
              <p class="eyebrow">Trace</p>
              <strong>执行过程</strong>
            </div>
            <div id="traceList" class="trace-list">
              <div class="empty-chat">发送一条消息后，这里会显示路由、规划、检索等过程。</div>
            </div>
          </section>

          <section class="response-card composer-card">
            <div class="response-head">
              <p class="eyebrow">Prompt</p>
              <strong>提问</strong>
            </div>
            <textarea id="query" placeholder="输入问题，例如：请比较上海浦东新区两份政策通知在支持对象和支持方向上的差异，并整理成要点。"></textarea>
            <label class="field slim grow">
              <span>Metadata Filters (JSON)</span>
              <input id="metadataFilters" placeholder='{"doc_category":"policy","region":"上海"}' />
            </label>
            <div class="live-status" id="agentStatus">等待发送请求...</div>
            <div class="composer-actions">
              <button id="sendChat">发送</button>
            </div>
          </section>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Evaluation</p>
            <h3>评估与 Benchmark</h3>
          </div>
          <div class="inline compact">
            <label class="field slim">
              <span>Top K</span>
              <input id="topK" type="number" min="1" max="20" value="3" />
            </label>
            <label class="field slim">
              <span>Candidate K</span>
              <input id="candidateK" type="number" min="1" max="100" value="12" />
            </label>
            <label class="field slim">
              <span>Strategy</span>
              <select id="strategy">
                <option value="hybrid_rerank">hybrid_rerank</option>
                <option value="dense_only">dense_only</option>
                <option value="dense_rerank">dense_rerank</option>
                <option value="hybrid_only">hybrid_only</option>
              </select>
            </label>
          </div>
        </div>

        <div class="inline wrap">
          <button id="runRetrievalEval" class="ghost">Retrieval Eval</button>
          <button id="runCompare" class="ghost">Baseline Compare</button>
          <button id="runGenerationEval" class="ghost">Generation Eval</button>
          <button id="runBenchmark" class="ghost">System Benchmark</button>
          <button id="showTestingPanel" class="ghost">测试环境重建</button>
        </div>

        <div id="evalStatus" class="live-status eval-status">选择一个评估功能后开始运行。</div>

        <section id="retrievalEvalPanel" class="dashboard-card eval-panel">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Metrics</p>
              <h4>Retrieval Eval</h4>
            </div>
          </div>
          <div id="retrievalHighlights" class="hero-metrics hero-metrics-2"></div>
          <div id="metricCards" class="metric-grid"></div>
          <pre id="retrievalEvalResult" class="result-box large"></pre>
        </section>

        <section id="comparePanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Compare</p>
              <h4>Baseline Compare</h4>
            </div>
          </div>
          <div id="compareChart" class="chart-panel empty-state">运行 Baseline Compare 后显示</div>
          <pre id="compareResult" class="result-box large"></pre>
        </section>

        <section id="generationEvalPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Generation</p>
              <h4>Generation Eval</h4>
            </div>
          </div>
          <pre id="generationEvalResult" class="result-box large"></pre>
        </section>

        <section id="benchmarkPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Benchmark</p>
              <h4>System Benchmark</h4>
            </div>
          </div>
          <div id="benchmarkHighlights" class="hero-metrics hero-metrics-1"></div>
          <div id="benchmarkChart" class="chart-panel empty-state">运行 System Benchmark 后显示</div>
          <pre id="benchmarkResult" class="result-box large"></pre>
        </section>

        <section id="testingPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Testing</p>
              <h4>测试环境重建</h4>
            </div>
          </div>
          <p class="helper-text">
            用于一键重新下载测试语料、清洗、入库并重建评估集，适合在新环境或测试数据被改乱后快速恢复。
          </p>
          <div class="compact-actions">
            <label class="check">
              <input id="forceDownload" type="checkbox" />
              <span>强制下载：忽略本地缓存，重新抓取测试文档</span>
            </label>
            <label class="check">
              <input id="runRetrievalEvalAfterRebuild" type="checkbox" checked />
              <span>自动评估：重建完成后顺手跑一次 retrieval eval</span>
            </label>
          </div>
          <div class="inline wrap">
            <button id="rebuildEnv">重建环境</button>
          </div>
          <pre id="rebuildResult" class="result-box large"></pre>
        </section>
      </section>
    </main>
  </div>
`;

const $ = (selector) => document.querySelector(selector);

const apiBaseInput = $("#apiBase");
const threadInput = $("#threadId");

function setRailOpen(open) {
  state.railOpen = open;
  document.body.dataset.railOpen = open ? "true" : "false";
}

function setActiveEvalAction(buttonId) {
  const ids = ["runRetrievalEval", "runCompare", "runGenerationEval", "runBenchmark", "showTestingPanel"];
  state.activeEvalAction = buttonId;
  ids.forEach((id) => {
    const button = $("#" + id);
    if (!button) return;
    button.classList.toggle("is-active", id === buttonId);
  });

  const panelMap = {
    runRetrievalEval: "retrievalEvalPanel",
    runCompare: "comparePanel",
    runGenerationEval: "generationEvalPanel",
    runBenchmark: "benchmarkPanel",
    showTestingPanel: "testingPanel",
  };
  Object.values(panelMap).forEach((panelId) => {
    $("#" + panelId)?.classList.add("hidden");
  });
  $("#" + panelMap[buttonId])?.classList.remove("hidden");
}

function formatNumber(value, digits = 4) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return Number(value).toFixed(digits);
}

function parseOptionalJson(raw) {
  const value = raw.trim();
  if (!value) return null;
  return JSON.parse(value);
}

function prettyPrint(target, payload) {
  target.textContent =
    typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
}

function addMessage(role, content) {
  state.messages.push({
    role,
    content,
    time: new Date().toLocaleTimeString("zh-CN", { hour12: false }),
  });
  renderMessages();
}

function renderMessages() {
  const messageList = $("#messageList");
  const messages = [...state.messages];

  if (state.streamingAnswer) {
    messages.push({
      role: "agent",
      content: state.streamingAnswer,
      time: "生成中",
      streaming: true,
    });
  }

  if (!messages.length) {
    messageList.innerHTML = `<div class="empty-chat">发送一条消息后，聊天记录会显示在这里。</div>`;
    return;
  }

  messageList.innerHTML = messages
    .map(
      (message) => `
        <article class="message-card ${message.role} ${message.streaming ? "streaming" : ""}">
          <header>
            <strong>${message.role === "user" ? "User" : "Agent"}</strong>
            <span>${message.time}</span>
          </header>
          <div class="message-body ${message.role === "agent" ? "markdown-body" : ""}">${
            message.role === "agent"
              ? marked.parse(message.content || "")
              : escapeHtml(message.content).replace(/\n/g, "<br/>")
          }</div>
        </article>
      `
    )
    .join("");
  messageList.scrollTop = messageList.scrollHeight;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function isTraceLine(line) {
  const trimmed = line.trim();
  if (!trimmed) return false;
  return /^(🧭|🛠️|✅|🔍|📎|💡|⚙️|🚦|📌|🔀|🧠|\[[^\]]+\])/.test(trimmed);
}

function splitStreamContent(buffer) {
  const lines = buffer.split("\n");
  const trace = [];
  const answer = [];

  for (const line of lines) {
    if (isTraceLine(line)) {
      trace.push(line.trim());
      continue;
    }
    answer.push(line);
  }

  return {
    trace,
    answer: answer.join("\n").trim(),
  };
}

function renderTrace(traceLines) {
  const container = $("#traceList");
  if (!traceLines.length) {
    container.innerHTML = `<div class="empty-chat">等待后端返回执行过程...</div>`;
    return;
  }

  container.innerHTML = traceLines
    .map(
      (line, index) => `
        <div class="trace-item">
          <span class="trace-step">${index + 1}</span>
          <div>${escapeHtml(line)}</div>
        </div>
      `
    )
    .join("");
}

function stopStatusTicker() {
  if (state.statusTimer) {
    clearInterval(state.statusTimer);
    state.statusTimer = null;
  }
}

function startStatusTicker() {
  stopStatusTicker();
  state.requestStartedAt = Date.now();
  const statusEl = $("#agentStatus");
  statusEl.textContent = "Agent 正在接收请求...";

  state.statusTimer = setInterval(() => {
    const elapsed = Math.round((Date.now() - state.requestStartedAt) / 1000);
    const lastTrace = state.activeTrace[state.activeTrace.length - 1];
    if (lastTrace) {
      statusEl.textContent = `${lastTrace} · ${elapsed}s`;
    } else {
      statusEl.textContent = `Agent 正在规划 / 检索 / 生成... · ${elapsed}s`;
    }
  }, 400);
}

function renderSummaryCards() {
  const retrievalCards = $("#retrievalHighlights");
  const benchmarkCards = $("#benchmarkHighlights");
  const retrieval = state.latestRetrievalMetrics;
  const benchmark = state.latestBenchmarkMetrics;

  const retrievalHighlights = [
    {
      label: "最近 Recall@K",
      value: retrieval ? formatNumber(retrieval.avg_recall_at_k, 4) : "待运行",
      tone: "warm",
    },
    {
      label: "最近 MRR",
      value: retrieval ? formatNumber(retrieval.mrr, 4) : "待运行",
      tone: "teal",
    },
  ];

  const benchmarkHighlights = [
    {
      label: "复杂任务时延",
      value: benchmark ? `${formatNumber(benchmark.complex_request_latency_ms, 2)} ms` : "待运行",
      tone: "dark",
    },
  ];

  retrievalCards.innerHTML = retrievalHighlights
    .map(
      (card) => `
        <div class="metric metric-${card.tone}">
          <span>${card.label}</span>
          <strong>${card.value}</strong>
        </div>
      `
    )
    .join("");

  benchmarkCards.innerHTML = benchmarkHighlights
    .map(
      (card) => `
        <div class="metric metric-${card.tone}">
          <span>${card.label}</span>
          <strong>${card.value}</strong>
        </div>
      `
    )
    .join("");
}

function renderMetricCards() {
  const container = $("#metricCards");
  const retrieval = state.latestRetrievalMetrics;
  const benchmark = state.latestBenchmarkMetrics;
  const cards = [
    ["Precision@K", retrieval?.avg_precision_at_k, 4],
    ["Recall@K", retrieval?.avg_recall_at_k, 4],
    ["MRR", retrieval?.mrr, 4],
    ["nDCG@K", retrieval?.ndcg_at_k, 4],
    ["Avg Query Latency", retrieval ? `${formatNumber(retrieval.avg_query_latency_ms, 2)} ms` : null, null],
    ["Complex Latency", benchmark ? `${formatNumber(benchmark.complex_request_latency_ms, 2)} ms` : null, null],
  ];

  container.innerHTML = cards
    .map(([label, value, digits]) => {
      const text = typeof value === "string" ? value : value == null ? "待运行" : formatNumber(value, digits || 4);
      return `
        <div class="stat-card">
          <span>${label}</span>
          <strong>${text}</strong>
        </div>
      `;
    })
    .join("");
}

function buildBar(label, value, max, suffix = "", precision = 4) {
  const width = max > 0 ? Math.max((value / max) * 100, 4) : 0;
  const display = typeof value === "number" ? `${value.toFixed(precision)}${suffix}` : value;
  return `
    <div class="bar-row">
      <div class="bar-meta">
        <strong>${label}</strong>
        <span>${display}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${width}%"></div>
      </div>
    </div>
  `;
}

function renderCompareChart() {
  const container = $("#compareChart");
  const report = state.latestCompareReport;
  if (!report?.baselines?.length) {
    container.className = "chart-panel empty-state";
    container.textContent = "运行 Baseline Compare 后显示";
    return;
  }

  const maxRecall = Math.max(...report.baselines.map((item) => item.avg_recall_at_k), 1);
  const maxMrr = Math.max(...report.baselines.map((item) => item.mrr), 1);
  const maxLatency = Math.max(...report.baselines.map((item) => item.avg_query_latency_ms), 1);

  container.className = "chart-panel";
  container.innerHTML = report.baselines
    .map(
      (item) => `
        <section class="compare-card">
          <h5>${item.strategy}</h5>
          ${buildBar("Recall", item.avg_recall_at_k, maxRecall)}
          ${buildBar("MRR", item.mrr, maxMrr)}
          ${buildBar("Latency", item.avg_query_latency_ms, maxLatency, " ms", 2)}
        </section>
      `
    )
    .join("");
}

function renderBenchmarkChart() {
  const container = $("#benchmarkChart");
  const metrics = state.latestBenchmarkMetrics;
  if (!metrics) {
    container.className = "chart-panel empty-state";
    container.textContent = "运行 System Benchmark 后显示";
    return;
  }

  const values = [
    ["Retrieval Avg", metrics.retrieval_avg_latency_ms],
    ["Retrieval P95", metrics.retrieval_p95_latency_ms],
    ["Simple Request", metrics.simple_request_latency_ms],
    ["Complex Request", metrics.complex_request_latency_ms],
  ];
  const max = Math.max(...values.map(([, value]) => value), 1);

  container.className = "chart-panel benchmark-layout";
  container.innerHTML = values.map(([label, value]) => buildBar(label, value, max, " ms", 2)).join("");
}

function syncDashboard() {
  renderSummaryCards();
  renderMetricCards();
  renderCompareChart();
  renderBenchmarkChart();
}

async function readStream(response, target) {
  if (!response.body) {
    throw new Error("stream body not available");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    target.textContent = buffer;
    target.scrollTop = target.scrollHeight;
    const parsed = splitStreamContent(buffer);
    state.activeTrace = parsed.trace;
    state.streamingAnswer = parsed.answer;
    renderTrace(parsed.trace);
    renderMessages();
  }
  return buffer;
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${state.apiBase}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `request failed: ${response.status}`);
  }
  return response.json();
}

apiBaseInput.addEventListener("change", () => {
  state.apiBase = apiBaseInput.value.trim() || "/api/v1";
  localStorage.setItem("agent-api-base", state.apiBase);
});

threadInput.addEventListener("change", () => {
  state.threadId = threadInput.value.trim();
  localStorage.setItem("agent-thread-id", state.threadId);
});

$("#regenThread").addEventListener("click", () => {
  state.threadId = createThreadId();
  threadInput.value = state.threadId;
  localStorage.setItem("agent-thread-id", state.threadId);
});

$("#clearChat").addEventListener("click", () => {
  state.messages = [];
  state.activeTrace = [];
  state.streamingAnswer = "";
  $("#traceList").innerHTML = `<div class="empty-chat">会话已清空。</div>`;
  $("#agentStatus").textContent = "会话已清空。";
  renderMessages();
});

async function submitChat() {
  const queryInput = $("#query");
  const query = queryInput.value.trim();
  if (!query) {
    $("#agentStatus").textContent = "请输入问题。";
    return;
  }

  state.activeTrace = [];
  state.streamingAnswer = "";
  renderTrace([]);
  startStatusTicker();
  addMessage("user", query);
  queryInput.value = "";

  try {
    const metadataFilters = parseOptionalJson($("#metadataFilters").value);
    const response = await fetch(`${state.apiBase}/chat/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        thread_id: state.threadId,
        user_id: $("#userId").value.trim(),
        task_mode: null,
        metadata_filters: metadataFilters,
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const bufferTarget = document.createElement("pre");
    const finalText = await readStream(response, bufferTarget);
    const parsed = splitStreamContent(finalText);
    renderTrace(parsed.trace);
    state.streamingAnswer = "";
    $("#agentStatus").textContent = "生成完成";
    addMessage("agent", parsed.answer || finalText || "空响应");
    stopStatusTicker();
  } catch (error) {
    stopStatusTicker();
    state.streamingAnswer = "";
    $("#agentStatus").textContent = `请求失败：${error.message}`;
    addMessage("agent", `请求失败：${error.message}`);
  }
}

$("#sendChat").addEventListener("click", submitChat);
$("#openRail").addEventListener("click", () => setRailOpen(!state.railOpen));
$("#closeRail").addEventListener("click", () => setRailOpen(false));

$("#query").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    submitChat();
  }
});

$("#uploadKnowledge").addEventListener("click", async () => {
  const file = $("#knowledgeFile").files[0];
  const resultBox = $("#uploadResult");
  if (!file) {
    resultBox.textContent = "请先选择文件。";
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${state.apiBase}/knowledge/upload`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    prettyPrint(resultBox, payload);
  } catch (error) {
    resultBox.textContent = `上传失败：${error.message}`;
  }
});

$("#rebuildEnv").addEventListener("click", async () => {
  const resultBox = $("#rebuildResult");
  setActiveEvalAction("showTestingPanel");
  $("#evalStatus").textContent = "正在重建测试环境...";
  resultBox.textContent = "正在重建测试环境...";

  try {
    const payload = await requestJson("/testing/rebuild", {
      method: "POST",
      body: JSON.stringify({
        force_download: $("#forceDownload").checked,
        run_retrieval_eval: $("#runRetrievalEvalAfterRebuild").checked,
      }),
    });
    prettyPrint(resultBox, payload);
    if (payload?.result?.retrieval_eval) {
      state.latestRetrievalMetrics = payload.result.retrieval_eval;
      syncDashboard();
    }
    $("#evalStatus").textContent = "测试环境重建完成。";
  } catch (error) {
    resultBox.textContent = `重建失败：${error.message}`;
    $("#evalStatus").textContent = `测试环境重建失败：${error.message}`;
  }
});

$("#runRetrievalEval").addEventListener("click", async () => {
  const resultBox = $("#retrievalEvalResult");
  setActiveEvalAction("runRetrievalEval");
  $("#evalStatus").textContent = "正在运行 Retrieval Eval...";
  resultBox.textContent = "正在运行 retrieval eval...";
  try {
    const payload = await requestJson("/eval/retrieval", {
      method: "POST",
      body: JSON.stringify({
        top_k: Number($("#topK").value),
        candidate_k: Number($("#candidateK").value),
        strategy: $("#strategy").value,
      }),
    });
    prettyPrint(resultBox, payload);
    state.latestRetrievalMetrics = payload.metrics;
    syncDashboard();
    $("#evalStatus").textContent = "Retrieval Eval 运行完成。";
  } catch (error) {
    resultBox.textContent = `retrieval eval 失败：${error.message}`;
    $("#evalStatus").textContent = `Retrieval Eval 失败：${error.message}`;
  }
});

$("#runCompare").addEventListener("click", async () => {
  const resultBox = $("#compareResult");
  setActiveEvalAction("runCompare");
  $("#evalStatus").textContent = "正在运行 Baseline Compare...";
  resultBox.textContent = "正在运行 baseline compare...";
  try {
    const payload = await requestJson("/eval/retrieval/compare", {
      method: "POST",
      body: JSON.stringify({
        top_k: Number($("#topK").value),
        candidate_k: Number($("#candidateK").value),
        strategy: $("#strategy").value,
      }),
    });
    prettyPrint(resultBox, payload);
    state.latestCompareReport = payload.report;
    const best = payload.report?.baselines?.find((item) => item.strategy === $("#strategy").value) ||
      payload.report?.baselines?.[payload.report?.baselines?.length - 1];
    if (best) {
      state.latestRetrievalMetrics = best;
    }
    syncDashboard();
    $("#evalStatus").textContent = "Baseline Compare 运行完成。";
  } catch (error) {
    resultBox.textContent = `compare 失败：${error.message}`;
    $("#evalStatus").textContent = `Baseline Compare 失败：${error.message}`;
  }
});

$("#runGenerationEval").addEventListener("click", async () => {
  const resultBox = $("#generationEvalResult");
  setActiveEvalAction("runGenerationEval");
  $("#evalStatus").textContent = "正在运行 Generation Eval...";
  resultBox.textContent = "正在运行 generation eval...";
  try {
    const payload = await requestJson("/eval/generation", {
      method: "POST",
      body: JSON.stringify({
        candidate_k: Number($("#candidateK").value),
      }),
    });
    prettyPrint(resultBox, payload);
    $("#evalStatus").textContent = "Generation Eval 运行完成。";
  } catch (error) {
    resultBox.textContent = `generation eval 失败：${error.message}`;
    $("#evalStatus").textContent = `Generation Eval 失败：${error.message}`;
  }
});

$("#runBenchmark").addEventListener("click", async () => {
  const resultBox = $("#benchmarkResult");
  setActiveEvalAction("runBenchmark");
  $("#evalStatus").textContent = "正在运行 System Benchmark...";
  resultBox.textContent = "正在运行 system benchmark...";
  try {
    const payload = await requestJson("/eval/benchmark", {
      method: "POST",
      body: JSON.stringify({
        candidate_k: Number($("#candidateK").value),
      }),
    });
    prettyPrint(resultBox, payload);
    state.latestBenchmarkMetrics = payload.metrics;
    syncDashboard();
    $("#evalStatus").textContent = "System Benchmark 运行完成。";
  } catch (error) {
    resultBox.textContent = `benchmark 失败：${error.message}`;
    $("#evalStatus").textContent = `System Benchmark 失败：${error.message}`;
  }
});

$("#showTestingPanel").addEventListener("click", () => {
  setActiveEvalAction("showTestingPanel");
  $("#evalStatus").textContent = "当前显示测试环境重建模块。";
});

renderMessages();
syncDashboard();
setRailOpen(false);
setActiveEvalAction("runRetrievalEval");
