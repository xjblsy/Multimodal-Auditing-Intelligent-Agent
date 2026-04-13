const state = {
  config: null,
  profile: null,
  allItems: [],
  visibleItems: [],
  selectedItemId: null,
  scenarios: [],
  selectedScenarioId: null,
  learningPath: null,
  dataSources: [],
  selectedDataSourceId: null,
  analysisResult: null,
  riskFactors: [],
  riskAssessmentResult: null,
  complianceStandards: [],
  complianceCheckResult: null,
  reportTemplates: [],
  reportResult: null,
};

const elements = {
  knowledgeCount: document.getElementById("knowledgeCount"),
  scenarioCount: document.getElementById("scenarioCount"),
  modelBadge: document.getElementById("modelBadge"),
  statusPill: document.getElementById("statusPill"),
  knowledgeList: document.getElementById("knowledgeList"),
  knowledgeDetail: document.getElementById("knowledgeDetail"),
  knowledgeSearchForm: document.getElementById("knowledgeSearchForm"),
  knowledgeQuery: document.getElementById("knowledgeQuery"),
  knowledgeIndustry: document.getElementById("knowledgeIndustry"),
  refreshKnowledgeBtn: document.getElementById("refreshKnowledgeBtn"),
  chatForm: document.getElementById("chatForm"),
  chatInput: document.getElementById("chatInput"),
  chatIndustry: document.getElementById("chatIndustry"),
  chatScenario: document.getElementById("chatScenario"),
  chatResponse: document.getElementById("chatResponse"),
  scenarioSelect: document.getElementById("scenarioSelect"),
  scenarioStageSelect: document.getElementById("scenarioStageSelect"),
  scenarioContext: document.getElementById("scenarioContext"),
  scenarioAnswer: document.getElementById("scenarioAnswer"),
  evaluateScenarioBtn: document.getElementById("evaluateScenarioBtn"),
  scenarioFeedback: document.getElementById("scenarioFeedback"),
  pathForm: document.getElementById("pathForm"),
  pathIndustry: document.getElementById("pathIndustry"),
  pathRole: document.getElementById("pathRole"),
  pathLevel: document.getElementById("pathLevel"),
  pathResult: document.getElementById("pathResult"),
  newItemBtn: document.getElementById("newItemBtn"),
  rebuildBtn: document.getElementById("rebuildBtn"),
  deleteItemBtn: document.getElementById("deleteItemBtn"),
  editorForm: document.getElementById("editorForm"),
  editorId: document.getElementById("editorId"),
  editorTitle: document.getElementById("editorTitle"),
  editorCategory: document.getElementById("editorCategory"),
  editorIndustries: document.getElementById("editorIndustries"),
  editorDifficulty: document.getElementById("editorDifficulty"),
  editorTags: document.getElementById("editorTags"),
  editorSummary: document.getElementById("editorSummary"),
  editorObjectives: document.getElementById("editorObjectives"),
  editorBody: document.getElementById("editorBody"),
  editorChecklist: document.getElementById("editorChecklist"),
  editorRedFlags: document.getElementById("editorRedFlags"),
  editorMistakes: document.getElementById("editorMistakes"),
  editorQuestions: document.getElementById("editorQuestions"),
  editorRelated: document.getElementById("editorRelated"),
  editorVisuals: document.getElementById("editorVisuals"),
  editorVideos: document.getElementById("editorVideos"),
  editorTables: document.getElementById("editorTables"),
  dataSourcesList: document.getElementById("dataSourcesList"),
  dataSourceForm: document.getElementById("dataSourceForm"),
  newDataSourceBtn: document.getElementById("newDataSourceBtn"),
  newDataSourceForm: document.getElementById("newDataSourceForm"),
  dsName: document.getElementById("dsName"),
  dsType: document.getElementById("dsType"),
  dsPath: document.getElementById("dsPath"),
  dsDescription: document.getElementById("dsDescription"),
  cancelDataSourceBtn: document.getElementById("cancelDataSourceBtn"),
  dataAnalysisResult: document.getElementById("dataAnalysisResult"),
  analysisContent: document.getElementById("analysisContent"),
  riskIndustry: document.getElementById("riskIndustry"),
  riskDataSource: document.getElementById("riskDataSource"),
  riskFactorsList: document.getElementById("riskFactorsList"),
  riskFactorForm: document.getElementById("riskFactorForm"),
  newRiskFactorBtn: document.getElementById("newRiskFactorBtn"),
  newRiskFactorForm: document.getElementById("newRiskFactorForm"),
  rfName: document.getElementById("rfName"),
  rfDescription: document.getElementById("rfDescription"),
  rfSeverity: document.getElementById("rfSeverity"),
  rfLikelihood: document.getElementById("rfLikelihood"),
  rfCategory: document.getElementById("rfCategory"),
  rfIndustry: document.getElementById("rfIndustry"),
  rfControls: document.getElementById("rfControls"),
  cancelRiskFactorBtn: document.getElementById("cancelRiskFactorBtn"),
  assessRiskBtn: document.getElementById("assessRiskBtn"),
  riskAssessmentResult: document.getElementById("riskAssessmentResult"),
  assessmentContent: document.getElementById("assessmentContent"),
  complianceStandardsList: document.getElementById("complianceStandardsList"),
  complianceStandardForm: document.getElementById("complianceStandardForm"),
  newComplianceStandardBtn: document.getElementById("newComplianceStandardBtn"),
  newComplianceStandardForm: document.getElementById("newComplianceStandardForm"),
  csName: document.getElementById("csName"),
  csDescription: document.getElementById("csDescription"),
  csCategory: document.getElementById("csCategory"),
  csVersion: document.getElementById("csVersion"),
  csEffectiveDate: document.getElementById("csEffectiveDate"),
  csRequirements: document.getElementById("csRequirements"),
  cancelComplianceStandardBtn: document.getElementById("cancelComplianceStandardBtn"),
  checkComplianceBtn: document.getElementById("checkComplianceBtn"),
  complianceEvidenceForm: document.getElementById("complianceEvidenceForm"),
  complianceStandardSelect: document.getElementById("complianceStandardSelect"),
  complianceEvidence: document.getElementById("complianceEvidence"),
  cancelComplianceCheckBtn: document.getElementById("cancelComplianceCheckBtn"),
  complianceCheckResult: document.getElementById("complianceCheckResult"),
  complianceContent: document.getElementById("complianceContent"),
  reportTemplatesList: document.getElementById("reportTemplatesList"),
  reportTemplateForm: document.getElementById("reportTemplateForm"),
  newReportTemplateBtn: document.getElementById("newReportTemplateBtn"),
  newReportTemplateForm: document.getElementById("newReportTemplateForm"),
  rtName: document.getElementById("rtName"),
  rtDescription: document.getElementById("rtDescription"),
  rtFormat: document.getElementById("rtFormat"),
  rtSections: document.getElementById("rtSections"),
  cancelReportTemplateBtn: document.getElementById("cancelReportTemplateBtn"),
  generateReportBtn: document.getElementById("generateReportBtn"),
  reportForm: document.getElementById("reportForm"),
  generateReportForm: document.getElementById("generateReportForm"),
  reportTemplateSelect: document.getElementById("reportTemplateSelect"),
  reportCompanyName: document.getElementById("reportCompanyName"),
  reportAuditPeriod: document.getElementById("reportAuditPeriod"),
  reportAuditDate: document.getElementById("reportAuditDate"),
  reportAuditor: document.getElementById("reportAuditor"),
  reportFindings: document.getElementById("reportFindings"),
  reportRecommendations: document.getElementById("reportRecommendations"),
  cancelReportBtn: document.getElementById("cancelReportBtn"),
  reportResult: document.getElementById("reportResult"),
  reportContent: document.getElementById("reportContent"),
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindEvents();
  await Promise.all([loadConfig(), loadProfile(), loadKnowledge(), loadScenarios(), loadDataSources(), loadRiskFactors(), loadComplianceStandards(), loadReportTemplates()]);
  if (state.visibleItems.length) {
    selectItem(state.visibleItems[0].id);
  }
  await createLearningPath();
  updateRiskDataSourceOptions();
  updateComplianceStandardOptions();
  updateReportTemplateOptions();
}

function bindEvents() {
  elements.knowledgeSearchForm.addEventListener("submit", handleKnowledgeSearch);
  elements.refreshKnowledgeBtn.addEventListener("click", () => loadKnowledge());
  elements.chatForm.addEventListener("submit", handleChatSubmit);
  elements.scenarioSelect.addEventListener("change", handleScenarioSelection);
  elements.scenarioStageSelect.addEventListener("change", renderScenarioContext);
  elements.evaluateScenarioBtn.addEventListener("click", handleScenarioEvaluate);
  elements.pathForm.addEventListener("submit", handlePathSubmit);
  elements.newItemBtn.addEventListener("click", resetEditor);
  elements.rebuildBtn.addEventListener("click", rebuildIndex);
  elements.deleteItemBtn.addEventListener("click", deleteCurrentItem);
  elements.editorForm.addEventListener("submit", saveItem);
  elements.newDataSourceBtn.addEventListener("click", showDataSourceForm);
  elements.cancelDataSourceBtn.addEventListener("click", hideDataSourceForm);
  elements.newDataSourceForm.addEventListener("submit", handleDataSourceSubmit);
  elements.newRiskFactorBtn.addEventListener("click", showRiskFactorForm);
  elements.cancelRiskFactorBtn.addEventListener("click", hideRiskFactorForm);
  elements.newRiskFactorForm.addEventListener("submit", handleRiskFactorSubmit);
  elements.assessRiskBtn.addEventListener("click", handleRiskAssessment);
  elements.riskIndustry.addEventListener("change", loadRiskFactors);
  elements.newComplianceStandardBtn.addEventListener("click", showComplianceStandardForm);
  elements.cancelComplianceStandardBtn.addEventListener("click", hideComplianceStandardForm);
  elements.newComplianceStandardForm.addEventListener("submit", handleComplianceStandardSubmit);
  elements.checkComplianceBtn.addEventListener("click", showComplianceEvidenceForm);
  elements.cancelComplianceCheckBtn.addEventListener("click", hideComplianceEvidenceForm);
  elements.complianceEvidenceForm.addEventListener("submit", handleComplianceCheck);
  elements.newReportTemplateBtn.addEventListener("click", showReportTemplateForm);
  elements.cancelReportTemplateBtn.addEventListener("click", hideReportTemplateForm);
  elements.newReportTemplateForm.addEventListener("submit", handleReportTemplateSubmit);
  elements.generateReportBtn.addEventListener("click", showReportForm);
  elements.cancelReportBtn.addEventListener("click", hideReportForm);
  elements.generateReportForm.addEventListener("submit", handleGenerateReport);
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadConfig() {
  state.config = await fetchJSON("/api/config");
  elements.modelBadge.textContent = `${state.config.model_provider}:${state.config.model_name}`;
  elements.chatIndustry.value = state.config.default_industry || "制造业";
  elements.pathIndustry.value = state.config.default_industry || "制造业";
  elements.statusPill.textContent = state.config.provider_ready ? "百炼在线模式" : "本地知识回退模式";
}

async function loadProfile() {
  state.profile = await fetchJSON("/api/profile");
}

async function loadKnowledge(query = "", industry = "") {
  const params = new URLSearchParams({ limit: "100" });
  if (query) params.set("query", query);
  if (industry) params.set("industry", industry);
  const data = await fetchJSON(`/api/knowledge?${params.toString()}`);
  state.visibleItems = data.items || [];

  if (!query && !industry) {
    state.allItems = state.visibleItems.slice();
  }
  if (!state.allItems.length && state.visibleItems.length) {
    state.allItems = state.visibleItems.slice();
  }

  renderKnowledgeList();
  updateMetrics();

  const currentStillVisible = state.visibleItems.some((item) => item.id === state.selectedItemId);
  if (!currentStillVisible) {
    state.selectedItemId = state.visibleItems[0]?.id || null;
  }
  renderKnowledgeDetail(getItemById(state.selectedItemId));
}

async function loadScenarios() {
  const data = await fetchJSON("/api/scenarios");
  state.scenarios = data.items || [];
  state.selectedScenarioId = state.scenarios[0]?.id || null;
  renderScenarioOptions();
  renderScenarioContext();
  updateMetrics();
}

function updateMetrics() {
  elements.knowledgeCount.textContent = String(state.allItems.length || state.visibleItems.length || 0);
  elements.scenarioCount.textContent = String(state.scenarios.length || 0);
}

function renderKnowledgeList() {
  if (!state.visibleItems.length) {
    elements.knowledgeList.innerHTML = `
      <div class="empty-state">
        <h3>没有命中结果</h3>
        <p>换个关键词，或者直接在下方编辑工坊里新增条目。</p>
      </div>
    `;
    return;
  }

  elements.knowledgeList.innerHTML = state.visibleItems
    .map((item) => {
      const chips = [
        `<span class="chip">${escapeHtml(item.category || "未分类")}</span>`,
        ...(item.industries || []).slice(0, 2).map((industry) => `<span class="chip alt">${escapeHtml(industry)}</span>`),
        `<span class="chip gold">${escapeHtml(item.difficulty || "中级")}</span>`,
      ].join("");
      return `
        <article class="knowledge-card ${item.id === state.selectedItemId ? "active" : ""}" data-id="${escapeHtml(item.id)}">
          <h3>${escapeHtml(item.title)}</h3>
          <div class="meta-row">${chips}</div>
          <p>${escapeHtml(item.summary || "暂无摘要")}</p>
        </article>
      `;
    })
    .join("");

  elements.knowledgeList.querySelectorAll(".knowledge-card").forEach((card) => {
    card.addEventListener("click", () => selectItem(card.dataset.id));
  });
}

function selectItem(itemId) {
  state.selectedItemId = itemId;
  renderKnowledgeList();
  const item = getItemById(itemId);
  renderKnowledgeDetail(item);
  if (item) {
    fillEditor(item);
  }
}

function renderKnowledgeDetail(item) {
  if (!item) {
    elements.knowledgeDetail.innerHTML = `
      <div class="empty-state">
        <h3>还没有选中知识条目</h3>
        <p>先在左侧选一个，或者在下方新建属于你的行业知识。</p>
      </div>
    `;
    return;
  }

  const sectionsHtml = (item.content_sections || [])
    .map(
      (section) => `
        <div class="section-card">
          <h4>${escapeHtml(section.heading)}</h4>
          <p>${escapeHtml(section.body)}</p>
        </div>
      `
    )
    .join("");

  elements.knowledgeDetail.innerHTML = `
    <div class="response-card">
      <div>
        <h3>${escapeHtml(item.title)}</h3>
        <div class="meta-row">
          <span class="chip">${escapeHtml(item.category || "未分类")}</span>
          ${(item.tags || []).map((tag) => `<span class="chip alt">${escapeHtml(tag)}</span>`).join("")}
        </div>
        <p>${escapeHtml(item.summary || "暂无摘要")}</p>
      </div>
      ${sectionsHtml}
      ${renderListBlock("检查清单", item.checklist || [])}
      ${renderListBlock("风险信号", item.red_flags || [])}
      ${renderListBlock("常见误区", item.common_mistakes || [])}
      ${renderQuestions(item.questions || [])}
      ${renderAssets(item.modalities || {})}
    </div>
  `;
}

function renderListBlock(title, items) {
  if (!items.length) return "";
  return `
    <div class="section-card">
      <h4>${escapeHtml(title)}</h4>
      <ul class="bullet-list">
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderQuestions(questions) {
  if (!questions.length) return "";
  return `
    <div class="section-card">
      <h4>常见问答</h4>
      ${questions
        .map(
          (item) => `
            <div class="mini-card">
              <p><strong>Q:</strong> ${escapeHtml(item.q || "")}</p>
              <p><strong>A:</strong> ${escapeHtml(item.a || "")}</p>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderAssets(modalities) {
  const visuals = modalities.visuals || [];
  const videos = modalities.videos || [];
  const tables = modalities.tables || [];
  if (!visuals.length && !videos.length && !tables.length) return "";

  return `
    <div class="section-card">
      <h4>多模态资源</h4>
      <div class="asset-grid">
        ${visuals.map(renderImageAsset).join("")}
        ${videos.map(renderVideoAsset).join("")}
        ${tables.map(renderTableAsset).join("")}
      </div>
    </div>
  `;
}

function renderImageAsset(asset) {
  return `
    <div class="asset-card">
      <h4>${escapeHtml(asset.title || "视觉材料")}</h4>
      ${asset.path ? `<img src="${escapeHtml(asset.path)}" alt="${escapeHtml(asset.title || "视觉材料")}" />` : ""}
      <p>${escapeHtml(asset.caption || "")}</p>
    </div>
  `;
}

function renderVideoAsset(asset) {
  const body = asset.url
    ? `<p><a href="${escapeHtml(asset.url)}" target="_blank" rel="noreferrer">打开视频链接</a></p>`
    : `<p class="muted">当前为占位卡，等你接入自己的视频资料。</p>`;
  return `
    <div class="asset-card">
      <h4>${escapeHtml(asset.title || "视频材料")}</h4>
      <p>${escapeHtml(asset.caption || "可挂接你自己的录屏、课程或项目复盘视频。")}</p>
      ${body}
    </div>
  `;
}

function renderTableAsset(asset) {
  const headers = asset.headers || [];
  const rows = asset.rows || [];
  return `
    <div class="asset-card">
      <h4>${escapeHtml(asset.title || "结构化表格")}</h4>
      <table>
        <thead>
          <tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function handleKnowledgeSearch(event) {
  event.preventDefault();
  await loadKnowledge(elements.knowledgeQuery.value.trim(), elements.knowledgeIndustry.value);
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const query = elements.chatInput.value.trim();
  if (!query) {
    alert("先输入一个你想请教的问题。");
    return;
  }

  elements.statusPill.textContent = "正在生成指导...";
  try {
    const result = await fetchJSON("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        industry: elements.chatIndustry.value,
        scenario_id: elements.chatScenario.value || null,
      }),
    });
    renderChatResponse(result);
    elements.statusPill.textContent = result.answer_source || "本地知识增强";
  } catch (error) {
    elements.statusPill.textContent = "生成失败";
    elements.chatResponse.innerHTML = `
      <div class="empty-state">
        <h3>暂时没成功</h3>
        <p>${escapeHtml(error.message)}</p>
      </div>
    `;
  }
}

function renderChatResponse(result) {
  const profileCard = result.profile
    ? `
      <div class="section-card">
        <h4>当前智能体配置</h4>
        <p><strong>${escapeHtml(result.profile.name || "")}</strong></p>
        <div class="meta-row">
          ${(result.profile.answer_sections || []).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}
        </div>
      </div>
    `
    : "";

  const citationsHtml = (result.citations || [])
    .map(
      (citation) => `
        <button class="ghost-btn citation-btn" data-id="${escapeHtml(citation.id)}">${escapeHtml(citation.title)}</button>
      `
    )
    .join("");

  elements.chatResponse.innerHTML = `
    <div class="response-card">
      <h3>智能指导结果</h3>
      <pre>${escapeHtml(result.answer || "")}</pre>
      ${profileCard}
      ${renderListBlock("审计思路", result.reasoning_frame || [])}
      ${renderListBlock("建议动作", result.recommended_actions || [])}
      ${renderListBlock("风险提醒", result.red_flags || [])}
      ${renderListBlock("继续学习", result.learning_suggestions || [])}
      ${
        citationsHtml
          ? `<div class="section-card"><h4>知识引用</h4><div class="meta-row">${citationsHtml}</div></div>`
          : ""
      }
      ${renderRelatedAssets(result.related_assets || [])}
      ${
        result.model_notice
          ? `<div class="mini-card muted"><p>模型提示：${escapeHtml(result.model_notice)}</p></div>`
          : ""
      }
    </div>
  `;

  elements.chatResponse.querySelectorAll(".citation-btn").forEach((button) => {
    button.addEventListener("click", () => selectItem(button.dataset.id));
  });
}

function renderRelatedAssets(assets) {
  if (!assets.length) return "";
  return `
    <div class="section-card">
      <h4>相关多模态材料</h4>
      <div class="asset-grid">
        ${assets
          .map((asset) => {
            if (asset.type === "image") return renderImageAsset(asset);
            if (asset.type === "table") return renderTableAsset(asset);
            return renderVideoAsset(asset);
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderScenarioOptions() {
  const optionsHtml = state.scenarios
    .map((scenario) => `<option value="${escapeHtml(scenario.id)}">${escapeHtml(scenario.title)}</option>`)
    .join("");
  elements.scenarioSelect.innerHTML = optionsHtml;
  elements.chatScenario.innerHTML = `<option value="">不绑定案例</option>${optionsHtml}`;
  if (state.selectedScenarioId) {
    elements.scenarioSelect.value = state.selectedScenarioId;
  }
  renderScenarioStages();
}

function handleScenarioSelection() {
  state.selectedScenarioId = elements.scenarioSelect.value;
  renderScenarioStages();
  renderScenarioContext();
}

function renderScenarioStages() {
  const scenario = getScenarioById(state.selectedScenarioId);
  const stages = scenario?.stages || [];
  elements.scenarioStageSelect.innerHTML = stages
    .map((stage) => `<option value="${escapeHtml(stage.id)}">${escapeHtml(stage.title)}</option>`)
    .join("");
}

function renderScenarioContext() {
  const scenario = getScenarioById(state.selectedScenarioId);
  if (!scenario) {
    elements.scenarioContext.innerHTML = "<p>暂无案例。</p>";
    return;
  }
  const currentStageId = elements.scenarioStageSelect.value || scenario.stages?.[0]?.id;
  const currentStage = (scenario.stages || []).find((stage) => stage.id === currentStageId) || scenario.stages?.[0];
  elements.scenarioContext.innerHTML = `
    <h3>${escapeHtml(scenario.title)}</h3>
    <p>${escapeHtml(scenario.background || "")}</p>
    ${
      currentStage
        ? `
          <div class="mini-card">
            <p><strong>${escapeHtml(currentStage.title)}</strong></p>
            <p>${escapeHtml(currentStage.task || "")}</p>
            <div class="meta-row">${(currentStage.evidence || []).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>
          </div>
        `
        : ""
    }
  `;
}

async function handleScenarioEvaluate() {
  const scenarioId = elements.scenarioSelect.value;
  const stageId = elements.scenarioStageSelect.value;
  const answer = elements.scenarioAnswer.value.trim();
  if (!scenarioId || !stageId || !answer) {
    alert("请先选择案例、阶段，并写下你的作答。");
    return;
  }

  const result = await fetchJSON(`/api/scenarios/${scenarioId}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stage_id: stageId, answer }),
  });

  elements.scenarioFeedback.innerHTML = `
    <h3>${escapeHtml(result.level)} · ${escapeHtml(String(result.score))} 分</h3>
    <div class="meta-row">
      ${(result.hits || []).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}
      ${(result.excellent_hits || []).map((item) => `<span class="chip gold">${escapeHtml(item)}</span>`).join("")}
    </div>
    <ul class="bullet-list">
      ${(result.feedback || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

async function handlePathSubmit(event) {
  event.preventDefault();
  await createLearningPath();
}

async function createLearningPath() {
  state.learningPath = await fetchJSON("/api/learning-path", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      industry: elements.pathIndustry.value,
      role: elements.pathRole.value.trim(),
      target_level: elements.pathLevel.value,
    }),
  });
  renderLearningPath();
}

function renderLearningPath() {
  const path = state.learningPath;
  if (!path) {
    elements.pathResult.innerHTML = "";
    return;
  }

  const skillChips = (path.skills || []).map((skill) => `<span class="chip">${escapeHtml(skill.name || "")}</span>`).join("");
  const lanes = (path.lanes || [])
    .map(
      (lane) => `
        <article class="lane-card">
          <h3>${escapeHtml(lane.stage)}</h3>
          ${(lane.items || [])
            .map(
              (item) => `
                <div class="mini-card">
                  <p><strong>${escapeHtml(item.title)}</strong></p>
                  <p>${escapeHtml(item.summary || "")}</p>
                </div>
              `
            )
            .join("")}
        </article>
      `
    )
    .join("");

  elements.pathResult.innerHTML = `
    <div class="response-card">
      <h3>${escapeHtml(path.industry)} / ${escapeHtml(path.target_level)} 学习路径</h3>
      <p><strong>当前教练：</strong>${escapeHtml(path.profile_name || "")}</p>
      <div class="meta-row">${skillChips}</div>
      <ul class="bullet-list">
        ${(path.strategy || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
      ${lanes}
    </div>
  `;
}

function fillEditor(item) {
  elements.editorId.value = item.id || "";
  elements.editorTitle.value = item.title || "";
  elements.editorCategory.value = item.category || "";
  elements.editorIndustries.value = (item.industries || []).join(", ");
  elements.editorDifficulty.value = item.difficulty || "";
  elements.editorTags.value = (item.tags || []).join(", ");
  elements.editorSummary.value = item.summary || "";
  elements.editorObjectives.value = (item.learning_objectives || []).join("\n");
  elements.editorBody.value = item.body_markdown || "";
  elements.editorChecklist.value = (item.checklist || []).join("\n");
  elements.editorRedFlags.value = (item.red_flags || []).join("\n");
  elements.editorMistakes.value = (item.common_mistakes || []).join("\n");
  elements.editorQuestions.value = prettyJson(item.questions || []);
  elements.editorRelated.value = (item.related_ids || []).join(", ");
  elements.editorVisuals.value = prettyJson(item.modalities?.visuals || []);
  elements.editorVideos.value = prettyJson(item.modalities?.videos || []);
  elements.editorTables.value = prettyJson(item.modalities?.tables || []);
}

function resetEditor() {
  elements.editorForm.reset();
  elements.editorId.value = "";
  elements.editorQuestions.value = "[]";
  elements.editorVisuals.value = "[]";
  elements.editorVideos.value = "[]";
  elements.editorTables.value = "[]";
}

async function saveItem(event) {
  event.preventDefault();
  let payload;
  try {
    payload = buildEditorPayload();
  } catch (error) {
    alert(error.message);
    return;
  }

  const itemId = elements.editorId.value.trim();
  const url = itemId ? `/api/knowledge/${encodeURIComponent(itemId)}` : "/api/knowledge";
  const method = itemId ? "PUT" : "POST";

  const saved = await fetchJSON(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await loadKnowledge();
  selectItem(saved.id);
  alert("知识条目已保存。");
}

async function deleteCurrentItem() {
  const itemId = elements.editorId.value.trim();
  if (!itemId) {
    alert("当前没有可删除的条目。");
    return;
  }
  if (!window.confirm(`确定删除条目「${itemId}」吗？`)) {
    return;
  }
  await fetchJSON(`/api/knowledge/${encodeURIComponent(itemId)}`, { method: "DELETE" });
  resetEditor();
  state.selectedItemId = null;
  await loadKnowledge();
  alert("条目已删除。");
}

async function rebuildIndex() {
  await fetchJSON("/api/rebuild-index", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  await Promise.all([loadKnowledge(), loadScenarios()]);
  alert("索引已重建。");
}

function buildEditorPayload() {
  return {
    title: elements.editorTitle.value.trim(),
    category: elements.editorCategory.value.trim(),
    industries: csvToArray(elements.editorIndustries.value),
    difficulty: elements.editorDifficulty.value.trim() || "中级",
    tags: csvToArray(elements.editorTags.value),
    summary: elements.editorSummary.value.trim(),
    learning_objectives: linesToArray(elements.editorObjectives.value),
    body_markdown: elements.editorBody.value.trim(),
    checklist: linesToArray(elements.editorChecklist.value),
    red_flags: linesToArray(elements.editorRedFlags.value),
    common_mistakes: linesToArray(elements.editorMistakes.value),
    questions: parseJSONArray(elements.editorQuestions.value, "问答 JSON"),
    related_ids: csvToArray(elements.editorRelated.value),
    modalities: {
      visuals: parseJSONArray(elements.editorVisuals.value, "视觉资源 JSON"),
      videos: parseJSONArray(elements.editorVideos.value, "视频资源 JSON"),
      tables: parseJSONArray(elements.editorTables.value, "表格资源 JSON"),
    },
  };
}

function parseJSONArray(raw, label) {
  try {
    const parsed = JSON.parse(raw || "[]");
    if (!Array.isArray(parsed)) {
      throw new Error(`${label} 必须是数组。`);
    }
    return parsed;
  } catch (error) {
    throw new Error(`${label} 格式不正确。`);
  }
}

function csvToArray(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function linesToArray(value) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function prettyJson(value) {
  return JSON.stringify(value || [], null, 2);
}

function getItemById(itemId) {
  return state.allItems.find((item) => item.id === itemId) || state.visibleItems.find((item) => item.id === itemId) || null;
}

function getScenarioById(scenarioId) {
  return state.scenarios.find((scenario) => scenario.id === scenarioId) || null;
}

async function loadDataSources() {
  const data = await fetchJSON("/api/data-sources");
  state.dataSources = data.items || [];
  renderDataSources();
}

function renderDataSources() {
  if (!state.dataSources.length) {
    elements.dataSourcesList.innerHTML = `
      <div class="empty-state">
        <h3>还没有数据源</h3>
        <p>点击上方「添加数据源」按钮，开始添加财务数据。</p>
      </div>
    `;
    return;
  }

  elements.dataSourcesList.innerHTML = state.dataSources
    .map((source) => {
      return `
        <article class="knowledge-card" data-id="${escapeHtml(source.id)}">
          <h3>${escapeHtml(source.name)}</h3>
          <div class="meta-row">
            <span class="chip">${escapeHtml(source.type)}</span>
            <span class="chip alt">${escapeHtml(source.last_updated)}</span>
          </div>
          <p>${escapeHtml(source.description || "暂无描述")}</p>
          <p><small>路径: ${escapeHtml(source.path)}</small></p>
          <div class="editor-actions">
            <button class="ghost-btn analyze-btn" data-id="${escapeHtml(source.id)}">分析数据</button>
            <button class="danger-btn delete-btn" data-id="${escapeHtml(source.id)}">删除</button>
          </div>
        </article>
      `;
    })
    .join("");

  elements.dataSourcesList.querySelectorAll(".analyze-btn").forEach((button) => {
    button.addEventListener("click", () => handleDataSourceAnalyze(button.dataset.id));
  });

  elements.dataSourcesList.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", () => handleDataSourceDelete(button.dataset.id));
  });
}

function showDataSourceForm() {
  elements.dataSourceForm.style.display = "block";
  elements.dataAnalysisResult.style.display = "none";
}

function hideDataSourceForm() {
  elements.dataSourceForm.style.display = "none";
  elements.newDataSourceForm.reset();
}

async function handleDataSourceSubmit(event) {
  event.preventDefault();
  const payload = {
    name: elements.dsName.value.trim(),
    type: elements.dsType.value,
    path: elements.dsPath.value.trim(),
    description: elements.dsDescription.value.trim()
  };

  try {
    await fetchJSON("/api/data-sources", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    hideDataSourceForm();
    await loadDataSources();
    alert("数据源已添加。");
  } catch (error) {
    alert(`添加数据源失败: ${error.message}`);
  }
}

async function handleDataSourceAnalyze(sourceId) {
  try {
    const result = await fetchJSON(`/api/data-sources/${sourceId}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    state.analysisResult = result;
    renderAnalysisResult();
  } catch (error) {
    alert(`分析数据失败: ${error.message}`);
  }
}

async function handleDataSourceDelete(sourceId) {
  if (!window.confirm("确定删除该数据源吗？")) {
    return;
  }
  try {
    await fetchJSON(`/api/data-sources/${sourceId}`, { method: "DELETE" });
    await loadDataSources();
    alert("数据源已删除。");
  } catch (error) {
    alert(`删除数据源失败: ${error.message}`);
  }
}

function renderAnalysisResult() {
  const result = state.analysisResult;
  if (!result) {
    elements.dataAnalysisResult.style.display = "none";
    return;
  }

  elements.dataAnalysisResult.style.display = "block";
  
  let metricsHtml = "";
  if (result.metrics) {
    metricsHtml = `
      <div class="section-card">
        <h4>财务指标</h4>
        <ul class="bullet-list">
          ${Object.entries(result.metrics)
            .map(([key, value]) => `<li>${escapeHtml(key)}: ${typeof value === 'number' ? value.toFixed(2) : value}</li>`)
            .join("")}
        </ul>
      </div>
    `;
  }

  let anomaliesHtml = "";
  if (result.anomalies && result.anomalies.length > 0) {
    anomaliesHtml = `
      <div class="section-card">
        <h4>异常检测</h4>
        <ul class="bullet-list">
          ${result.anomalies.map((anomaly) => `<li>类型: ${escapeHtml(anomaly.type)}, 偏差: ${anomaly.deviation.toFixed(2)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  let recommendationsHtml = "";
  if (result.recommendations && result.recommendations.length > 0) {
    recommendationsHtml = `
      <div class="section-card">
        <h4>审计建议</h4>
        <ul class="bullet-list">
          ${result.recommendations.map((rec) => `<li>${escapeHtml(rec)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  elements.analysisContent.innerHTML = `
    <div class="response-card">
      ${metricsHtml}
      ${anomaliesHtml}
      ${recommendationsHtml}
    </div>
  `;
}

async function loadRiskFactors() {
  const data = await fetchJSON("/api/risk-factors");
  state.riskFactors = data.items || [];
  // 按行业筛选
  const industry = elements.riskIndustry.value;
  const filteredFactors = state.riskFactors.filter(factor => factor.industry === industry || factor.industry === "通用");
  renderRiskFactors(filteredFactors);
}

function renderRiskFactors(factors) {
  if (!factors.length) {
    elements.riskFactorsList.innerHTML = `
      <div class="empty-state">
        <h3>还没有风险因素</h3>
        <p>点击上方「添加风险因素」按钮，开始添加审计风险因素。</p>
      </div>
    `;
    return;
  }

  elements.riskFactorsList.innerHTML = factors
    .map((factor) => {
      return `
        <article class="knowledge-card" data-id="${escapeHtml(factor.id)}">
          <h3>${escapeHtml(factor.name)}</h3>
          <div class="meta-row">
            <span class="chip">${escapeHtml(factor.category)}</span>
            <span class="chip alt">${escapeHtml(factor.industry)}</span>
            <span class="chip gold">严重程度: ${factor.severity}</span>
            <span class="chip gold">可能性: ${factor.likelihood}</span>
          </div>
          <p>${escapeHtml(factor.description || "暂无描述")}</p>
          ${factor.controls && factor.controls.length > 0 ? `
            <div class="section-card">
              <h4>控制措施</h4>
              <ul class="bullet-list">
                ${factor.controls.map(control => `<li>${escapeHtml(control)}</li>`).join("")}
              </ul>
            </div>
          ` : ""}
          <div class="editor-actions">
            <button class="danger-btn delete-btn" data-id="${escapeHtml(factor.id)}">删除</button>
          </div>
        </article>
      `;
    })
    .join("");

  elements.riskFactorsList.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", () => handleRiskFactorDelete(button.dataset.id));
  });
}

function showRiskFactorForm() {
  elements.riskFactorForm.style.display = "block";
  elements.riskAssessmentResult.style.display = "none";
}

function hideRiskFactorForm() {
  elements.riskFactorForm.style.display = "none";
  elements.newRiskFactorForm.reset();
}

async function handleRiskFactorSubmit(event) {
  event.preventDefault();
  const controls = elements.rfControls.value.split("\n").map(line => line.trim()).filter(Boolean);
  const payload = {
    name: elements.rfName.value.trim(),
    description: elements.rfDescription.value.trim(),
    severity: parseInt(elements.rfSeverity.value),
    likelihood: parseInt(elements.rfLikelihood.value),
    category: elements.rfCategory.value.trim(),
    industry: elements.rfIndustry.value,
    controls: controls
  };

  try {
    await fetchJSON("/api/risk-factors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    hideRiskFactorForm();
    await loadRiskFactors();
    alert("风险因素已添加。");
  } catch (error) {
    alert(`添加风险因素失败: ${error.message}`);
  }
}

async function handleRiskFactorDelete(riskId) {
  if (!window.confirm("确定删除该风险因素吗？")) {
    return;
  }
  try {
    await fetchJSON(`/api/risk-factors/${riskId}`, { method: "DELETE" });
    await loadRiskFactors();
    alert("风险因素已删除。");
  } catch (error) {
    alert(`删除风险因素失败: ${error.message}`);
  }
}

async function handleRiskAssessment() {
  const payload = {
    industry: elements.riskIndustry.value,
    data_source_id: elements.riskDataSource.value || null
  };

  try {
    const result = await fetchJSON("/api/risk-assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.riskAssessmentResult = result;
    renderRiskAssessmentResult();
  } catch (error) {
    alert(`风险评估失败: ${error.message}`);
  }
}

function renderRiskAssessmentResult() {
  const result = state.riskAssessmentResult;
  if (!result) {
    elements.riskAssessmentResult.style.display = "none";
    return;
  }

  elements.riskAssessmentResult.style.display = "block";
  
  let riskLevel = "低";
  if (result.overall_risk >= 4) {
    riskLevel = "高";
  } else if (result.overall_risk >= 3) {
    riskLevel = "中";
  }

  let riskFactorsHtml = "";
  if (result.risk_factors && result.risk_factors.length > 0) {
    riskFactorsHtml = `
      <div class="section-card">
        <h4>风险因素</h4>
        <ul class="bullet-list">
          ${result.risk_factors.map(factor => `
            <li>
              ${escapeHtml(factor.name)} (严重程度: ${factor.severity}, 可能性: ${factor.likelihood})
              ${factor.controls && factor.controls.length > 0 ? 
                `<ul><li>控制措施: ${factor.controls.slice(0, 3).join(", ")}</li></ul>` : 
                ""
              }
            </li>
          `).join("")}
        </ul>
      </div>
    `;
  }

  let recommendationsHtml = "";
  if (result.recommendations && result.recommendations.length > 0) {
    recommendationsHtml = `
      <div class="section-card">
        <h4>审计建议</h4>
        <ul class="bullet-list">
          ${result.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  let industryRisksHtml = "";
  if (result.industry_specific_risks && result.industry_specific_risks.length > 0) {
    industryRisksHtml = `
      <div class="section-card">
        <h4>行业特定风险</h4>
        <ul class="bullet-list">
          ${result.industry_specific_risks.map(risk => `<li>${escapeHtml(risk)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  elements.assessmentContent.innerHTML = `
    <div class="response-card">
      <div class="meta-row">
        <span class="chip gold">整体风险等级: ${riskLevel}</span>
        <span class="chip">风险评分: ${result.overall_risk}/5</span>
      </div>
      ${riskFactorsHtml}
      ${industryRisksHtml}
      ${recommendationsHtml}
    </div>
  `;
}

function updateRiskDataSourceOptions() {
  const optionsHtml = state.dataSources
    .map(source => `<option value="${escapeHtml(source.id)}">${escapeHtml(source.name)}</option>`)
    .join("");
  elements.riskDataSource.innerHTML = `<option value="">不使用数据源</option>${optionsHtml}`;
}

async function loadComplianceStandards() {
  const data = await fetchJSON("/api/compliance-standards");
  state.complianceStandards = data.items || [];
  renderComplianceStandards();
  updateComplianceStandardOptions();
}

function renderComplianceStandards() {
  if (!state.complianceStandards.length) {
    elements.complianceStandardsList.innerHTML = `
      <div class="empty-state">
        <h3>还没有合规标准</h3>
        <p>点击上方「添加合规标准」按钮，开始添加审计合规标准。</p>
      </div>
    `;
    return;
  }

  elements.complianceStandardsList.innerHTML = state.complianceStandards
    .map((standard) => {
      return `
        <article class="knowledge-card" data-id="${escapeHtml(standard.id)}">
          <h3>${escapeHtml(standard.name)}</h3>
          <div class="meta-row">
            <span class="chip">${escapeHtml(standard.category)}</span>
            <span class="chip alt">${escapeHtml(standard.version)}</span>
            <span class="chip gold">${escapeHtml(standard.effective_date)}</span>
          </div>
          <p>${escapeHtml(standard.description || "暂无描述")}</p>
          ${standard.requirements && standard.requirements.length > 0 ? `
            <div class="section-card">
              <h4>要求</h4>
              <ul class="bullet-list">
                ${standard.requirements.map(req => `<li>${escapeHtml(req)}</li>`).join("")}
              </ul>
            </div>
          ` : ""}
          <div class="editor-actions">
            <button class="danger-btn delete-btn" data-id="${escapeHtml(standard.id)}">删除</button>
          </div>
        </article>
      `;
    })
    .join("");

  elements.complianceStandardsList.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", () => handleComplianceStandardDelete(button.dataset.id));
  });
}

function showComplianceStandardForm() {
  elements.complianceStandardForm.style.display = "block";
  elements.complianceEvidenceForm.style.display = "none";
  elements.complianceCheckResult.style.display = "none";
}

function hideComplianceStandardForm() {
  elements.complianceStandardForm.style.display = "none";
  elements.newComplianceStandardForm.reset();
}

async function handleComplianceStandardSubmit(event) {
  event.preventDefault();
  const requirements = elements.csRequirements.value.split("\n").map(line => line.trim()).filter(Boolean);
  const payload = {
    name: elements.csName.value.trim(),
    description: elements.csDescription.value.trim(),
    category: elements.csCategory.value,
    version: elements.csVersion.value.trim(),
    effective_date: elements.csEffectiveDate.value,
    requirements: requirements
  };

  try {
    await fetchJSON("/api/compliance-standards", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    hideComplianceStandardForm();
    await loadComplianceStandards();
    alert("合规标准已添加。");
  } catch (error) {
    alert(`添加合规标准失败: ${error.message}`);
  }
}

async function handleComplianceStandardDelete(standardId) {
  if (!window.confirm("确定删除该合规标准吗？")) {
    return;
  }
  try {
    await fetchJSON(`/api/compliance-standards/${standardId}`, { method: "DELETE" });
    await loadComplianceStandards();
    alert("合规标准已删除。");
  } catch (error) {
    alert(`删除合规标准失败: ${error.message}`);
  }
}

function showComplianceEvidenceForm() {
  elements.complianceEvidenceForm.style.display = "block";
  elements.complianceStandardForm.style.display = "none";
  elements.complianceCheckResult.style.display = "none";
}

function hideComplianceEvidenceForm() {
  elements.complianceEvidenceForm.style.display = "none";
}

async function handleComplianceCheck(event) {
  event.preventDefault();
  let evidence;
  try {
    evidence = JSON.parse(elements.complianceEvidence.value);
  } catch (error) {
    alert("审计证据格式不正确，请输入有效的JSON格式。");
    return;
  }

  const payload = {
    standard_id: elements.complianceStandardSelect.value || null,
    evidence: evidence
  };

  try {
    const result = await fetchJSON("/api/compliance-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.complianceCheckResult = result;
    renderComplianceCheckResult();
  } catch (error) {
    alert(`合规性检查失败: ${error.message}`);
  }
}

function renderComplianceCheckResult() {
  const result = state.complianceCheckResult;
  if (!result) {
    elements.complianceCheckResult.style.display = "none";
    return;
  }

  elements.complianceCheckResult.style.display = "block";
  
  if (result.results) {
    // 多个标准的检查结果
    let resultsHtml = result.results.map(res => {
      let status = res.compliant ? "合规" : "不合规";
      let statusClass = res.compliant ? "chip green" : "chip red";
      
      let issuesHtml = "";
      if (res.issues && res.issues.length > 0) {
        issuesHtml = `
          <div class="section-card">
            <h4>问题</h4>
            <ul class="bullet-list">
              ${res.issues.map(issue => `<li>${escapeHtml(issue)}</li>`).join("")}
            </ul>
          </div>
        `;
      }

      let recommendationsHtml = "";
      if (res.recommendations && res.recommendations.length > 0) {
        recommendationsHtml = `
          <div class="section-card">
            <h4>建议</h4>
            <ul class="bullet-list">
              ${res.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join("")}
            </ul>
          </div>
        `;
      }

      let evidenceRequiredHtml = "";
      if (res.evidence_required && res.evidence_required.length > 0) {
        evidenceRequiredHtml = `
          <div class="section-card">
            <h4>所需证据</h4>
            <ul class="bullet-list">
              ${res.evidence_required.map(evidence => `<li>${escapeHtml(evidence)}</li>`).join("")}
            </ul>
          </div>
        `;
      }

      return `
        <div class="response-card">
          <h3>${escapeHtml(res.standard_name)}</h3>
          <div class="meta-row">
            <span class="${statusClass}">${status}</span>
          </div>
          ${issuesHtml}
          ${recommendationsHtml}
          ${evidenceRequiredHtml}
        </div>
      `;
    }).join("");

    elements.complianceContent.innerHTML = resultsHtml;
  } else {
    // 单个标准的检查结果
    let status = result.compliant ? "合规" : "不合规";
    let statusClass = result.compliant ? "chip green" : "chip red";

    let issuesHtml = "";
    if (result.issues && result.issues.length > 0) {
      issuesHtml = `
        <div class="section-card">
          <h4>问题</h4>
          <ul class="bullet-list">
            ${result.issues.map(issue => `<li>${escapeHtml(issue)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    let recommendationsHtml = "";
    if (result.recommendations && result.recommendations.length > 0) {
      recommendationsHtml = `
        <div class="section-card">
          <h4>建议</h4>
          <ul class="bullet-list">
            ${result.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    let evidenceRequiredHtml = "";
    if (result.evidence_required && result.evidence_required.length > 0) {
      evidenceRequiredHtml = `
        <div class="section-card">
          <h4>所需证据</h4>
          <ul class="bullet-list">
            ${result.evidence_required.map(evidence => `<li>${escapeHtml(evidence)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    elements.complianceContent.innerHTML = `
      <div class="response-card">
        <h3>${escapeHtml(result.standard_name)}</h3>
        <div class="meta-row">
          <span class="${statusClass}">${status}</span>
        </div>
        ${issuesHtml}
        ${recommendationsHtml}
        ${evidenceRequiredHtml}
      </div>
    `;
  }
}

function updateComplianceStandardOptions() {
  const optionsHtml = state.complianceStandards
    .map(standard => `<option value="${escapeHtml(standard.id)}">${escapeHtml(standard.name)}</option>`)
    .join("");
  elements.complianceStandardSelect.innerHTML = `<option value="">全部标准</option>${optionsHtml}`;
}

async function loadReportTemplates() {
  const data = await fetchJSON("/api/report-templates");
  state.reportTemplates = data.items || [];
  renderReportTemplates();
  updateReportTemplateOptions();
}

function renderReportTemplates() {
  if (!state.reportTemplates.length) {
    elements.reportTemplatesList.innerHTML = `
      <div class="empty-state">
        <h3>还没有报告模板</h3>
        <p>点击上方「添加报告模板」按钮，开始添加审计报告模板。</p>
      </div>
    `;
    return;
  }

  elements.reportTemplatesList.innerHTML = state.reportTemplates
    .map((template) => {
      return `
        <article class="knowledge-card" data-id="${escapeHtml(template.id)}">
          <h3>${escapeHtml(template.name)}</h3>
          <div class="meta-row">
            <span class="chip">${escapeHtml(template.format)}</span>
            <span class="chip alt">${template.sections.length} 个部分</span>
          </div>
          <p>${escapeHtml(template.description || "暂无描述")}</p>
          <div class="editor-actions">
            <button class="danger-btn delete-btn" data-id="${escapeHtml(template.id)}">删除</button>
          </div>
        </article>
      `;
    })
    .join("");

  elements.reportTemplatesList.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", () => handleReportTemplateDelete(button.dataset.id));
  });
}

function showReportTemplateForm() {
  elements.reportTemplateForm.style.display = "block";
  elements.reportForm.style.display = "none";
  elements.reportResult.style.display = "none";
}

function hideReportTemplateForm() {
  elements.reportTemplateForm.style.display = "none";
  elements.newReportTemplateForm.reset();
}

async function handleReportTemplateSubmit(event) {
  event.preventDefault();
  let sections;
  try {
    sections = JSON.parse(elements.rtSections.value);
  } catch (error) {
    alert("Sections格式不正确，请输入有效的JSON格式。");
    return;
  }
  
  const payload = {
    name: elements.rtName.value.trim(),
    description: elements.rtDescription.value.trim(),
    sections: sections,
    format: elements.rtFormat.value
  };

  try {
    await fetchJSON("/api/report-templates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    hideReportTemplateForm();
    await loadReportTemplates();
    alert("报告模板已添加。");
  } catch (error) {
    alert(`添加报告模板失败: ${error.message}`);
  }
}

async function handleReportTemplateDelete(templateId) {
  if (!window.confirm("确定删除该报告模板吗？")) {
    return;
  }
  try {
    await fetchJSON(`/api/report-templates/${templateId}`, { method: "DELETE" });
    await loadReportTemplates();
    alert("报告模板已删除。");
  } catch (error) {
    alert(`删除报告模板失败: ${error.message}`);
  }
}

function showReportForm() {
  elements.reportForm.style.display = "block";
  elements.reportTemplateForm.style.display = "none";
  elements.reportResult.style.display = "none";
}

function hideReportForm() {
  elements.reportForm.style.display = "none";
  elements.generateReportForm.reset();
}

async function handleGenerateReport(event) {
  event.preventDefault();
  const templateId = elements.reportTemplateSelect.value;
  if (!templateId) {
    alert("请选择报告模板。");
    return;
  }
  
  const findings = elements.reportFindings.value.split("\n").map(line => line.trim()).filter(Boolean);
  const recommendations = elements.reportRecommendations.value.split("\n").map(line => line.trim()).filter(Boolean);
  
  const payload = {
    template_id: templateId,
    company_name: elements.reportCompanyName.value.trim(),
    audit_period: elements.reportAuditPeriod.value.trim(),
    audit_date: elements.reportAuditDate.value,
    auditor: elements.reportAuditor.value.trim(),
    findings: findings,
    recommendations: recommendations
  };

  try {
    const result = await fetchJSON("/api/generate-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.reportResult = result;
    renderReportResult();
  } catch (error) {
    alert(`生成报告失败: ${error.message}`);
  }
}

function renderReportResult() {
  const result = state.reportResult;
  if (!result) {
    elements.reportResult.style.display = "none";
    return;
  }

  elements.reportResult.style.display = "block";
  
  elements.reportContent.innerHTML = `
    <div class="response-card">
      <h3>报告生成成功</h3>
      <p>报告已保存到: <strong>${escapeHtml(result.report_path)}</strong></p>
      <p>您可以在文件系统中找到该报告。</p>
    </div>
  `;
}

function updateReportTemplateOptions() {
  const optionsHtml = state.reportTemplates
    .map(template => `<option value="${escapeHtml(template.id)}">${escapeHtml(template.name)}</option>`)
    .join("");
  elements.reportTemplateSelect.innerHTML = `<option value="">选择模板</option>${optionsHtml}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
