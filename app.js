const state = {
  config: null,
  profile: null,
  messages: [],
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
  renderChatMessages();
}

function bindEvents() {
  // 聊天表单提交
  elements.chatForm.addEventListener("submit", handleChatSubmit);
  
  // 文件上传
  elements.uploadBtn.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", handleFileSelect);
  
  // 拖拽上传
  elements.uploadArea.addEventListener("dragover", handleDragOver);
  elements.uploadArea.addEventListener("drop", handleDrop);
  elements.uploadArea.addEventListener("click", () => elements.fileInput.click());
}

async function fetchJSON(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Request failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
}

async function loadConfig() {
  try {
    // 模拟加载配置
    state.config = {
      model_provider: "mock",
      model_name: "qwen-flash",
      default_industry: "制造业",
      provider_ready: false
    };
    elements.modelBadge.textContent = `${state.config.model_provider}:${state.config.model_name}`;
    elements.chatIndustry.value = state.config.default_industry || "制造业";
    elements.statusPill.textContent = state.config.provider_ready ? "百炼在线模式" : "本地知识增强";
  } catch (error) {
    console.error("Failed to load config:", error);
    // 使用默认配置
    state.config = {
      model_provider: "mock",
      model_name: "qwen-flash",
      default_industry: "制造业",
      provider_ready: false
    };
  }
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const query = elements.chatInput.value.trim();
  if (!query) {
    alert("请输入问题");
    return;
  }

  // 添加用户消息
  addMessage("user", query);
  elements.chatInput.value = "";
  elements.statusPill.textContent = "正在生成回答...";

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    const mockResponse = {
      answer: "这是一个模拟回答。在实际应用中，这里会显示大模型的真实回答。",
      answer_source: "本地知识增强"
    };
    addMessage("bot", mockResponse.answer);
    elements.statusPill.textContent = mockResponse.answer_source;
  } catch (error) {
    console.error("Chat error:", error);
    addMessage("bot", `错误: ${error.message}`);
    elements.statusPill.textContent = "生成失败";
  }
}

function addMessage(type, content) {
  state.messages.push({ type, content, timestamp: new Date() });
  renderChatMessages();
}

function renderChatMessages() {
  if (state.messages.length === 0) {
    elements.chatResponse.innerHTML = `
      <div class="empty-state">
        <h3>从真实问题开始</h3>
        <p>系统会结合知识库、案例和多模态材料，给出审计切入路径、证据建议和学习延伸。</p>
      </div>
    `;
    return;
  }

  elements.chatResponse.innerHTML = state.messages
    .map((message) => {
      return `
        <div class="message ${message.type}">
          <div class="message-content">
            ${escapeHtml(message.content)}
          </div>
        </div>
      `;
    })
    .join("");

  // 滚动到底部
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

function handleDrop(event) {
  event.preventDefault();
  elements.uploadArea.classList.remove("dragover");
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    uploadFiles(files);
  }
}

function uploadFiles(files) {
  // 显示上传进度
  elements.uploadProgress.style.display = "block";
  elements.uploadStatus.style.display = "none";
  state.uploadProgress = 0;
  updateProgress();

  // 模拟上传过程
  const uploadInterval = setInterval(() => {
    state.uploadProgress += 10;
    updateProgress();
    if (state.uploadProgress >= 100) {
      clearInterval(uploadInterval);
      setTimeout(() => {
        elements.uploadProgress.style.display = "none";
        elements.uploadStatus.style.display = "block";
        elements.uploadMessage.textContent = `成功上传 ${files.length} 个文件到知识库`;
        // 重置文件输入
        elements.fileInput.value = "";
      }, 500);
    }
  }, 300);
}

function updateProgress() {
  elements.progressFill.style.width = `${state.uploadProgress}%`;
  elements.progressText.textContent = `上传中... ${state.uploadProgress}%`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}