import { useEffect, useMemo, useRef, useState } from "react";
import { marked } from "marked";

type Role = "user" | "assistant";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
  traces: string[];
  createdAt: number;
};

type PaePlanStep = {
  stepId: string;
  capability: string;
  goal: string;
  status?: string;
};

type PaeExecutionStep = {
  stepId: string;
  status: string;
  goal: string;
};

type ParsedPaeTrace = {
  active: boolean;
  entered: boolean;
  planning: boolean;
  reflecting: boolean;
  generating: boolean;
  completed: boolean;
  currentStepId: string | null;
  planSteps: PaePlanStep[];
  executionSteps: PaeExecutionStep[];
  reflectionSteps: Array<{ stepId: string; status: string }>;
  raw: string[];
};

type CombinedPaeStep = {
  stepId: string;
  capability: string;
  goal: string;
  status: string;
};

type UploadState = {
  filename: string;
  chunksInserted: number;
  source: string;
} | null;

type RuntimeSkillAsset = {
  filename: string;
  content: string;
};

type RuntimeAssets = {
  agents_md: string;
  soul_md: string;
  memory_md: string;
  skills: RuntimeSkillAsset[];
};

const TRACE_PREFIXES = [
  ">",
  "🧠",
  "🧭",
  "📝",
  "🛠️",
  "🔁",
  "📎",
  "✍️",
  "✅",
  "⚠️",
  "❌",
  "💾",
  "🌐",
  "🔎",
  "⏱️",
];

function uid(): string {
  const randomUUID = globalThis.crypto?.randomUUID?.bind(globalThis.crypto);
  if (randomUUID) return randomUUID();
  const randomPart = Math.random().toString(36).slice(2, 10);
  return `id-${Date.now()}-${randomPart}`;
}

function isTraceBlock(text: string) {
  return TRACE_PREFIXES.some((prefix) => text.startsWith(prefix)) || /^-+\s*step[_-]?\d+/i.test(text);
}

function renderMarkdown(content: string) {
  return { __html: marked.parse(content) as string };
}

function splitThinkingContent(content: string): { thought: string; answer: string } {
  if (!content) return { thought: "", answer: "" };
  const start = content.indexOf("<think>");
  if (start === -1) return { thought: "", answer: content };
  const end = content.indexOf("</think>", start + 7);
  if (end === -1) {
    return {
      thought: content.slice(start + 7).trim(),
      answer: content.slice(0, start).trim(),
    };
  }
  const before = content.slice(0, start).trim();
  const thought = content.slice(start + 7, end).trim();
  const after = content.slice(end + 8).trim();
  return {
    thought,
    answer: [before, after].filter(Boolean).join("\n\n").trim(),
  };
}

function createAssistantPlaceholder(): ChatMessage {
  return {
    id: uid(),
    role: "assistant",
    content: "",
    traces: [],
    createdAt: Date.now(),
  };
}

function parsePaeTrace(traces: string[]): ParsedPaeTrace {
  const parsed: ParsedPaeTrace = {
    active: false,
    entered: false,
    planning: false,
    reflecting: false,
    generating: false,
    completed: false,
    currentStepId: null,
    planSteps: [],
    executionSteps: [],
    reflectionSteps: [],
    raw: traces,
  };

  for (const trace of traces) {
    if (trace.includes("[PAE调用]") || trace.includes("[计划模式]")) {
      parsed.active = true;
      parsed.entered = true;
      continue;
    }
    if (trace.startsWith("📝 [任务规划]")) {
      parsed.active = true;
      parsed.planning = true;
      continue;
    }
    if (/^-+\s*step[_-]?\d+/i.test(trace)) {
      const [, stepId = "", capability = "", goal = ""] = trace.split("|").map((item) => item.trim().replace(/^- /, ""));
      if (stepId) {
        parsed.planSteps.push({ stepId, capability, goal });
        parsed.active = true;
      }
      continue;
    }
    if (trace.startsWith("🛠️ [步骤开始]")) {
      const [, payload = ""] = trace.split("] ");
      const [stepId = ""] = payload.split("|").map((item) => item.trim());
      parsed.currentStepId = stepId || null;
      parsed.active = true;
      continue;
    }
    if (trace.startsWith("🛠️ [步骤执行]")) {
      const [, payload = ""] = trace.split("] ");
      const [stepId = "", status = "", goal = ""] = payload.split("|").map((item) => item.trim());
      parsed.executionSteps.push({ stepId, status, goal });
      if (parsed.currentStepId === stepId) {
        parsed.currentStepId = null;
      }
      parsed.active = true;
      continue;
    }
    if (trace.startsWith("🔁 [反思修正]")) {
      parsed.active = true;
      parsed.reflecting = true;
      continue;
    }
    if (trace.startsWith("📎 [反思结果]")) {
      const [, payload = ""] = trace.split("] ");
      const [stepId = "", status = ""] = payload.split("|").map((item) => item.trim());
      parsed.reflectionSteps.push({ stepId, status });
      parsed.active = true;
      continue;
    }
    if (trace.startsWith("✍️ [答案生成]")) {
      parsed.active = true;
      parsed.generating = true;
      continue;
    }
    if (trace.startsWith("✅ [PAE完成]")) {
      parsed.active = true;
      parsed.completed = true;
    }
  }

  if (parsed.planSteps.length > 0) {
    parsed.active = true;
    parsed.entered = true;
    parsed.planning = true;
  }
  if (parsed.executionSteps.length > 0) {
    parsed.active = true;
  }
  if (parsed.reflectionSteps.length > 0) {
    parsed.active = true;
    parsed.reflecting = true;
  }
  if (parsed.completed && parsed.planSteps.length > 0) {
    parsed.entered = true;
    parsed.planning = true;
    parsed.generating = true;
  }

  return parsed;
}

function buildCombinedPaeSteps(parsed: ParsedPaeTrace): CombinedPaeStep[] {
  const executionByStep = new Map(parsed.executionSteps.map((step) => [step.stepId, step]));
  return parsed.planSteps.map((step) => ({
    stepId: step.stepId,
    capability: step.capability,
    goal: step.goal,
    status: executionByStep.get(step.stepId)?.status ?? "pending",
  }));
}

export default function App() {
  const [apiBase, setApiBase] = useState("/api/v2");
  const [threadId] = useState(uid());
  const [userId, setUserId] = useState("");
  const [modelChoice, setModelChoice] = useState("local_qwen");
  const [forcePlan, setForcePlan] = useState(false);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadState, setUploadState] = useState<UploadState>(null);
  const [runtimeAssets, setRuntimeAssets] = useState<RuntimeAssets>({
    agents_md: "",
    soul_md: "",
    memory_md: "",
    skills: [],
  });
  const [assetsLoading, setAssetsLoading] = useState(false);
  const [assetsSaving, setAssetsSaving] = useState(false);
  const [error, setError] = useState("");
  const [toastMessage, setToastMessage] = useState("");
  const [activeTraceMessageId, setActiveTraceMessageId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showTracePanel, setShowTracePanel] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const toastTimerRef = useRef<number | null>(null);

  const activeTraceMessage = useMemo(
    () =>
      messages.find((message) => message.id === activeTraceMessageId) ??
      [...messages].reverse().find((message) => message.role === "assistant") ??
      null,
    [activeTraceMessageId, messages],
  );
  const activePaeTrace = useMemo(
    () => parsePaeTrace(activeTraceMessage?.traces ?? []),
    [activeTraceMessage],
  );
  const combinedPaeSteps = useMemo(
    () => buildCombinedPaeSteps(activePaeTrace),
    [activePaeTrace],
  );

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }, [query]);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > 960) {
        setShowSidebar(false);
        setShowTracePanel(false);
      }
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(() => {
    void loadRuntimeAssets();
  }, [apiBase]);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

  function showToast(message: string) {
    setToastMessage(message);
    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current);
    }
    toastTimerRef.current = window.setTimeout(() => {
      setToastMessage("");
      toastTimerRef.current = null;
    }, 2200);
  }

  async function loadRuntimeAssets() {
    setAssetsLoading(true);
    try {
      const response = await fetch(`${apiBase}/runtime/assets`);
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = (await response.json()) as RuntimeAssets;
      setRuntimeAssets({
        agents_md: data.agents_md ?? "",
        soul_md: data.soul_md ?? "",
        memory_md: data.memory_md ?? "",
        skills: Array.isArray(data.skills) ? data.skills : [],
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "运行时资产加载失败");
    } finally {
      setAssetsLoading(false);
    }
  }

  async function saveRuntimeAssets() {
    setAssetsSaving(true);
    setError("");
    try {
      const response = await fetch(`${apiBase}/runtime/assets`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(runtimeAssets),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = (await response.json()) as RuntimeAssets;
      setRuntimeAssets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "运行时资产保存失败");
    } finally {
      setAssetsSaving(false);
    }
  }

  async function handleSkillUpload(files: FileList | null) {
    if (!files?.length) return;
    setAssetsSaving(true);
    setError("");
    try {
      const uploaded = await Promise.all(
        Array.from(files).map(async (file) => ({
          filename: file.name,
          content: await file.text(),
        })),
      );

      const mergedMap = new Map(runtimeAssets.skills.map((skill) => [skill.filename, skill]));
      for (const skill of uploaded) {
        mergedMap.set(skill.filename, skill);
      }
      const nextAssets: RuntimeAssets = {
        ...runtimeAssets,
        skills: Array.from(mergedMap.values()).sort((a, b) => a.filename.localeCompare(b.filename)),
      };

      const response = await fetch(`${apiBase}/runtime/assets`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(nextAssets),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = (await response.json()) as RuntimeAssets;
      setRuntimeAssets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "技能上传失败");
    } finally {
      setAssetsSaving(false);
    }
  }

  async function handleUpload(file: File) {
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${apiBase}/knowledge/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      setUploadState({
        filename: data.filename ?? file.name,
        chunksInserted: data.chunks_inserted ?? 0,
        source: data.source ?? file.name,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  }

  async function handleSend() {
    if (!userId.trim()) {
      showToast("请先在菜单里填写 User ID");
      return;
    }
    if (!query.trim() || isSending) return;

    setError("");
    setIsSending(true);

    const userMessage: ChatMessage = {
      id: uid(),
      role: "user",
      content: query.trim(),
      traces: [],
      createdAt: Date.now(),
    };
    const assistantPlaceholder = createAssistantPlaceholder();
    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setActiveTraceMessageId(assistantPlaceholder.id);
    setQuery("");

    try {
      const response = await fetch(`${apiBase}/chat/agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: userMessage.content,
          thread_id: threadId,
          user_id: userId.trim(),
          plan_mode: forcePlan ? "strict_plan" : "auto",
          model_choice: modelChoice,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(await response.text());
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const pushBlock = (block: string) => {
        const trimmed = block.trim();
        if (!trimmed) return;
        setMessages((prev) =>
          prev.map((message) => {
            if (message.id !== assistantPlaceholder.id) return message;
            if (isTraceBlock(trimmed)) {
              if (message.traces[message.traces.length - 1] === trimmed) return message;
              return { ...message, traces: [...message.traces, trimmed] };
            }
            return {
              ...message,
              content: message.content ? `${message.content}\n\n${trimmed}` : trimmed,
            };
          }),
        );
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() ?? "";
        for (const block of blocks) pushBlock(block);
      }

      const finalChunk = buffer.trim();
      if (finalChunk) pushBlock(finalChunk);
    } catch (err) {
      const message = err instanceof Error ? err.message : "请求失败";
      setError(message);
      setMessages((prev) =>
        prev.map((item) =>
          item.id === assistantPlaceholder.id
            ? {
                ...item,
                traces: [...item.traces, `❌ 请求失败：${message}`],
                content: item.content || "请求失败，请检查后端服务或重试。",
              }
            : item,
        ),
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${showSidebar ? "open" : ""}`}>
        <div className="brand sidebar-brand">
          <div className="brand-badge">IA</div>
          <div>
            <div className="brand-title">InsightAgentPro</div>
            <div className="brand-subtitle">Agent Runtime Studio</div>
          </div>
          <button className="drawer-close" type="button" onClick={() => setShowSidebar(false)}>
            关闭
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Workspace</div>
          <label className="field compact">
            <span>API Base</span>
            <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
          </label>
          <label className="field compact">
            <span>User ID</span>
            <input
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="请先在菜单里填写 User ID"
              className={!userId.trim() ? "required" : ""}
            />
            <div className="field-note field-note-strong">填写 User ID 以启用长期记忆</div>
          </label>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title sidebar-title-compact">Persona &amp; MD Memory</div>
          <div className="asset-card">
            <label className="field compact">
              <span>AGENTS.md</span>
              <textarea
                rows={4}
                className="runtime-asset-textarea"
                value={runtimeAssets.agents_md}
                onChange={(e) => setRuntimeAssets((prev) => ({ ...prev, agents_md: e.target.value }))}
                placeholder={assetsLoading ? "加载中..." : "AGENTS.md"}
              />
            </label>
            <label className="field compact">
              <span>SOUL.md</span>
              <textarea
                rows={4}
                className="runtime-asset-textarea"
                value={runtimeAssets.soul_md}
                onChange={(e) => setRuntimeAssets((prev) => ({ ...prev, soul_md: e.target.value }))}
                placeholder={assetsLoading ? "加载中..." : "SOUL.md"}
              />
            </label>
            <label className="field compact">
              <span>MEMORY.md</span>
              <textarea
                rows={5}
                className="runtime-asset-textarea"
                value={runtimeAssets.memory_md}
                onChange={(e) => setRuntimeAssets((prev) => ({ ...prev, memory_md: e.target.value }))}
                placeholder={assetsLoading ? "加载中..." : "MEMORY.md"}
              />
            </label>
            <button
              className="secondary-button sidebar-save-button sidebar-save-button-compact sidebar-action-button"
              type="button"
              onClick={() => void saveRuntimeAssets()}
              disabled={assetsLoading || assetsSaving}
            >
              {assetsSaving ? "保存中..." : "Save Runtime Setup"}
            </button>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Skills</div>
          <div className="asset-card">
            <div className="skill-chip-list">
              {runtimeAssets.skills.map((skill) => (
                <span key={skill.filename} className="skill-chip">
                  {skill.filename}
                </span>
              ))}
              {!runtimeAssets.skills.length ? <span className="skill-empty">暂无已加载 Skills</span> : null}
            </div>
            <label className="upload-box compact skill-upload-box sidebar-action-button">
              <input
                type="file"
                accept=".md,text/markdown,text/plain"
                multiple
                onChange={(e) => {
                  void handleSkillUpload(e.target.files);
                  e.currentTarget.value = "";
                }}
              />
              <span>{assetsSaving ? "上传中..." : "上传 Skills"}</span>
            </label>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Knowledge Base</div>
          <div className="asset-card">
            <label className="upload-box compact upload-box-small sidebar-action-button">
              <input
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void handleUpload(file);
                }}
              />
              <span>{uploading ? "上传中..." : "上传文件到知识库"}</span>
            </label>
            {uploadState ? (
              <div className="upload-result">
                <div>{uploadState.filename}</div>
                <div>{uploadState.chunksInserted} chunks</div>
              </div>
            ) : null}
          </div>
        </div>

        {error ? <div className="error-card">{error}</div> : null}
      </aside>

      <main className="chat-column">
        <header className="chat-header compact-header">
          <div className="chat-header-row">
            <button className="mobile-toggle" type="button" onClick={() => setShowSidebar(true)}>
              菜单
            </button>
            <h1>Chat</h1>
            <button className="mobile-toggle" type="button" onClick={() => setShowTracePanel(true)}>
              运行
            </button>
          </div>
        </header>

        <section className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h2>开始一个新对话</h2>
              <p>填写 User ID 后直接提问。</p>
            </div>
          ) : null}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`message-row ${message.role}`}
              onClick={() => message.role === "assistant" && setActiveTraceMessageId(message.id)}
            >
              {(() => {
                const parsedPae = message.role === "assistant" ? parsePaeTrace(message.traces) : null;
                const { thought, answer } =
                  message.role === "assistant"
                    ? splitThinkingContent(message.content || "")
                    : { thought: "", answer: message.content || "" };
                const showCollapsedThought = Boolean(thought && answer);
                const bodyContent = answer || (thought ? "" : message.content || "处理中...");

                return (
                  <>
                    <div className="avatar">{message.role === "user" ? "你" : "AI"}</div>
                    <div className={`message-card ${message.role}`}>
                      <div className="message-meta">
                        <span>{message.role === "user" ? "You" : "Assistant"}</span>
                        {message.role === "assistant" ? (
                          <span className="trace-count">{message.traces.length} trace</span>
                        ) : null}
                      </div>
                      {message.role === "assistant" && parsedPae?.active ? (
                        <div className="pae-badge">PAE</div>
                      ) : null}
                      {message.role === "assistant" && thought ? (
                        <details className="thought-block" open={!showCollapsedThought}>
                          <summary>
                            <span className="thought-summary-collapsed">▸ 思考过程（展开）</span>
                            <span className="thought-summary-open">▾ 思考过程（折叠）</span>
                          </summary>
                          <div
                            className="thought-body"
                            dangerouslySetInnerHTML={renderMarkdown(thought)}
                          />
                        </details>
                      ) : null}
                      <div
                        className="message-body"
                        dangerouslySetInnerHTML={renderMarkdown(bodyContent)}
                      />
                    </div>
                  </>
                );
              })()}
            </article>
          ))}
          <div ref={bottomRef} />
        </section>

        <footer className="composer">
          <div className="composer-shell">
            <textarea
              ref={textareaRef}
              rows={1}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={userId.trim() ? "Type a message..." : "请先在菜单里填写 User ID"}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void handleSend();
                }
              }}
            />
            <div className="composer-inner-toolbar">
              <label className="inline-select">
                <span className="toolbar-label">模型</span>
                <select value={modelChoice} onChange={(e) => setModelChoice(e.target.value)}>
                  <option value="local_qwen">Local Qwen</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="minimax">MiniMax M2.7</option>
                </select>
              </label>
              <button
                className={`toggle-button ${forcePlan ? "active" : ""}`}
                type="button"
                onClick={() => setForcePlan((value) => !value)}
              >
                <span className="toggle-full">强制 Plan-and-Execute 模式</span>
                <span className="toggle-short">强制 PAE</span>
              </button>
              <button
                className="primary-button"
                onClick={() => void handleSend()}
                disabled={!query.trim() || isSending}
              >
                {isSending ? "发送中" : "发送"}
              </button>
            </div>
          </div>
        </footer>
      </main>

      <aside className={`trace-panel ${showTracePanel ? "open" : ""}`}>
        <div className="trace-header run-header">
          <div>
            <h2>Agent Run</h2>
            {activeTraceMessage?.traces.length ? (
              <p>{activePaeTrace.active ? "Running" : "Trace Stream"}</p>
            ) : null}
          </div>
          <button className="drawer-close" type="button" onClick={() => setShowTracePanel(false)}>
            关闭
          </button>
        </div>
        <div className="trace-guide">
          <p>采用 ReAct 主循环，Auto 模式下自动判断进入 Plan-and-Execute 模式，也可手动强制开启。</p>
          <p>发送消息后，这里会流式显示推理、工具调用和 PAE 过程。</p>
        </div>
        <div className="trace-list">
          {activeTraceMessage?.traces.length ? (
            activePaeTrace.active ? (
              <div className="run-panel">
                <section className="run-section">
                  <div className="run-section-title">Execution Stages</div>
                  <div className="run-stage-list">
                    <div className={`run-stage ${activePaeTrace.entered ? "done" : ""}`}>进入 PAE</div>
                    <div className={`run-stage ${activePaeTrace.planning ? "done" : ""}`}>生成计划</div>
                    <div className={`run-stage ${activePaeTrace.executionSteps.length ? "done" : ""}`}>执行步骤</div>
                    <div className={`run-stage ${activePaeTrace.reflecting ? "done" : ""}`}>反思修正</div>
                    <div className={`run-stage ${activePaeTrace.generating ? "done" : ""}`}>生成答案</div>
                    <div className={`run-stage ${activePaeTrace.completed ? "done" : ""}`}>返回主循环</div>
                  </div>
                </section>

                {combinedPaeSteps.length ? (
                  <section className="run-section">
                    <div className="run-section-title">Plan & Execution</div>
                    <div className="run-step-list">
                      {combinedPaeSteps.map((step, index) => (
                        <div
                          key={`plan-${step.stepId}`}
                          className={`run-step-card ${activePaeTrace.currentStepId === step.stepId ? "active" : ""}`}
                        >
                          <div className="run-step-index">Step {index + 1}</div>
                          <div className="run-step-main">
                            <div className="run-step-top">
                              <strong>{step.goal}</strong>
                              <span>{activePaeTrace.currentStepId === step.stepId ? "running" : step.status}</span>
                            </div>
                            <div className="run-capability-chip">{step.capability}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}

                {activePaeTrace.reflectionSteps.length ? (
                  <section className="run-section">
                    <div className="run-section-title">Reflection</div>
                    <div className="run-step-list">
                      {activePaeTrace.reflectionSteps.map((step, index) => (
                        <div key={`reflection-${step.stepId}-${index}`} className="run-step-card reflection">
                          <div className="run-step-main">
                            <div className="run-step-top">
                              <strong>{step.stepId}</strong>
                              <span>{step.status}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}
              </div>
            ) : (
              activeTraceMessage.traces.map((trace, index) => (
                <pre key={`${activeTraceMessage.id}-${index}`} className="trace-item">
                  {trace}
                </pre>
              ))
            )
          ) : (
            <div className="trace-empty">尚无运行记录。</div>
          )}
        </div>
      </aside>
      {(showSidebar || showTracePanel) ? (
        <button
          className="drawer-overlay"
          type="button"
          aria-label="关闭抽屉"
          onClick={() => {
            setShowSidebar(false);
            setShowTracePanel(false);
          }}
        />
      ) : null}
      {toastMessage ? <div className="toast-message">{toastMessage}</div> : null}
    </div>
  );
}
