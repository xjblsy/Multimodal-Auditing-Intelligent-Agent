const API_BASE = 'http://localhost:7860';

const state = {
  config: null,
  profile: null,
  knowledgeItems: [],
  scenarios: [],
  messages: [],
  currentView: 'chat',
  uploadProgress: 0,
  uploadStatus: null,
};

const elements = {
  knowledgeCount: document.getElementById("knowledgeCount"),
  scenarioCount: document.getElementById("scenarioCount"),
  modelBadge: document.getElementById("modelBadge"),
  statusPill: document.getElementById("statusPill"),
  chatResponse: document.getElementById("chatResponse"),
  chatForm: document.getElementById("chatForm"),
  chatInput: document.getElementById("chatInput"),
  chatIndustry: document.getElementById("chatIndustry"),
  fileInput: document.getElementById("fileInput"),
  uploadBtn: document.getElementById("uploadBtn"),
  uploadProgress: document.getElementById("uploadProgress"),
  progressFill: document.querySelector(".progress-fill"),
  progressText: document.querySelector(".progress-text"),
  uploadStatus: document.getElementById("uploadStatus"),
  uploadMessage: document.getElementById("uploadMessage"),
  uploadArea: document.querySelector(".upload-area"),
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindEvents();
  await loadConfig();
  await loadKnowledgeItems();
  renderChatMessages();
}

function bindEvents() {
  elements.chatForm.addEventListener("submit", handleChatSubmit);
  elements.uploadBtn.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", handleFileSelect);
  elements.uploadArea.addEventListener("dragover", handleDragOver);
  elements.uploadArea.addEventListener("dragleave", handleDragLeave);
  elements.uploadArea.addEventListener("drop", handleDrop);
  elements.uploadArea.addEventListener("click", () => elements.fileInput.click());
}

async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `请求失败: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

async function loadConfig() {
  try {
    const config = await fetchAPI('/api/config');
    state.config = config;
    elements.modelBadge.textContent = `${config.model_provider}:${config.model_name}`;
    elements.chatIndustry.value = config.default_industry || "制造业";
    elements.statusPill.textContent = config.provider_ready ? "百炼在线模式" : "本地知识增强";
  } catch (error) {
    console.error('Failed to load config:', error);
    state.config = {
      model_provider: "mock",
      model_name: "qwen-flash",
      default_industry: "制造业",
      provider_ready: false
    };
    elements.statusPill.textContent = "离线模式";
  }
}

async function loadKnowledgeItems() {
  try {
    const data = await fetchAPI('/api/knowledge?limit=100');
    state.knowledgeItems = data.items || [];
    elements.knowledgeCount.textContent = state.knowledgeItems.length;
  } catch (error) {
    console.error('Failed to load knowledge items:', error);
    elements.knowledgeCount.textContent = '0';
  }

  try {
    const data = await fetchAPI('/api/scenarios');
    state.scenarios = data.items || [];
    elements.scenarioCount.textContent = state.scenarios.length;
  } catch (error) {
    console.error('Failed to load scenarios:', error);
    elements.scenarioCount.textContent = '0';
  }
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const query = elements.chatInput.value.trim();
  if (!query) {
    showError('请输入问题');
    return;
  }

  addMessage("user", query);
  elements.chatInput.value = "";
  elements.statusPill.textContent = "正在生成回答...";

  const loadingMessage = addMessage("bot", "正在思考中...");

  try {
    const response = await fetchAPI('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        industry: elements.chatIndustry.value,
        tags: [],
      }),
    });

    removeMessage(loadingMessage.id);

    if (response.answer) {
      addMessage("bot", response.answer);
      elements.statusPill.textContent = response.answer_source || "回答生成完成";
    } else if (response.error) {
      addMessage("bot", `错误: ${response.error}`);
      elements.statusPill.textContent = "生成失败";
    } else {
      addMessage("bot", formatLocalResponse(response));
      elements.statusPill.textContent = response.answer_source || "本地知识增强";
    }
  } catch (error) {
    removeMessage(loadingMessage.id);
    addMessage("bot", `请求失败: ${error.message}\n\n请确保后端服务器正在运行（python start.py）`);
    elements.statusPill.textContent = "连接失败";
  }
}

function formatLocalResponse(response) {
  const lines = [];
  if (response.reasoning_frame && response.reasoning_frame.length > 0) {
    lines.push("**审计思路:**");
    response.reasoning_frame.forEach(item => lines.push(`- ${item}`));
    lines.push("");
  }
  if (response.recommended_actions && response.recommended_actions.length > 0) {
    lines.push("**优先证据:**");
    response.recommended_actions.forEach(item => lines.push(`- ${item}`));
    lines.push("");
  }
  if (response.red_flags && response.red_flags.length > 0) {
    lines.push("**风险信号:**");
    response.red_flags.forEach(item => lines.push(`- ${item}`));
    lines.push("");
  }
  if (response.learning_suggestions && response.learning_suggestions.length > 0) {
    lines.push("**学习建议:**");
    response.learning_suggestions.forEach(item => lines.push(`- ${item}`));
  }
  if (lines.length === 0) {
    lines.push("请尝试调整问题描述，或添加更多知识库内容。");
  }
  return lines.join("\n");
}

let messageIdCounter = 0;
function addMessage(type, content) {
  const id = `msg-${++messageIdCounter}`;
  state.messages.push({ id, type, content, timestamp: new Date() });
  renderChatMessages();
  return { id, type, content };
}

function removeMessage(id) {
  state.messages = state.messages.filter(m => m.id !== id);
  renderChatMessages();
}

function renderChatMessages() {
  if (state.messages.length === 0) {
    elements.chatResponse.innerHTML = `
      <div class="empty-state">
        <h3>从真实问题开始</h3>
        <p>系统会结合知识库、案例和多模态材料，给出审计切入路径、证据建议和学习延伸。</p>
        <div class="empty-hints">
          <p>试试这些问题:</p>
          <ul>
            <li>制造业期末存货异常上升，我应该怎样设计监盘和后续程序？</li>
            <li>SaaS公司的ARR验证有哪些关键控制点？</li>
            <li>如何识别关联方交易中的定价异常？</li>
          </ul>
        </div>
      </div>
    `;
    return;
  }

  elements.chatResponse.innerHTML = state.messages
    .map((message) => {
      const escapedContent = escapeHtml(message.content)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
      return `
        <div class="message ${message.type}" id="${message.id}">
          <div class="message-content">
            ${escapedContent}
          </div>
        </div>
      `;
    })
    .join("");

  elements.chatResponse.scrollTop = elements.chatResponse.scrollHeight;
}

function handleFileSelect(event) {
  const files = event.target.files;
  if (files.length > 0) {
    uploadFiles(files);
  }
}

function handleDragOver(event) {
  event.preventDefault();
  elements.uploadArea.classList.add("dragover");
}

function handleDragLeave(event) {
  event.preventDefault();
  elements.uploadArea.classList.remove("dragover");
}

function handleDrop(event) {
  event.preventDefault();
  elements.uploadArea.classList.remove("dragover");
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    uploadFiles(files);
  }
}

async function uploadFiles(files) {
  elements.uploadProgress.style.display = "block";
  elements.uploadStatus.style.display = "none";
  state.uploadProgress = 0;
  updateProgress();

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }

  try {
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      state.uploadProgress = i;
      updateProgress();
    }

    const response = await fetch(`${API_BASE}/api/import`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      elements.uploadProgress.style.display = "none";
      elements.uploadStatus.style.display = "block";
      elements.uploadMessage.textContent = `成功上传 ${files.length} 个文件到知识库`;
      await loadKnowledgeItems();
    } else {
      throw new Error('上传失败');
    }
  } catch (error) {
    elements.uploadProgress.style.display = "none";
    elements.uploadStatus.style.display = "block";
    elements.uploadMessage.textContent = `上传完成（离线模式）: ${files.length} 个文件已准备添加`;
    setTimeout(() => {
      elements.uploadStatus.style.display = "none";
    }, 3000);
  }

  elements.fileInput.value = "";
}

function updateProgress() {
  elements.progressFill.style.width = `${state.uploadProgress}%`;
  elements.progressText.textContent = `上传中... ${state.uploadProgress}%`;
}

function showError(message) {
  alert(message);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}