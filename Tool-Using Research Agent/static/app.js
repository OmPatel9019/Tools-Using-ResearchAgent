document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('research-form');
  const queryInput = document.getElementById('query-input');
  const submitBtn = document.getElementById('submit-btn');
  const chips = document.querySelectorAll('.chip');

  const progressSection = document.getElementById('progress-section');
  const timeline = document.getElementById('timeline');
  const stepBadge = document.getElementById('step-badge');

  const resultSection = document.getElementById('result-section');
  const reportContent = document.getElementById('report-content');
  const resourcesGrid = document.getElementById('resources-grid');
  const resourcesPill = document.getElementById('resources-pill');
  const auditBadge = document.getElementById('audit-badge');
  const metaSourcesCount = document.getElementById('meta-sources-count');
  const copyReportBtn = document.getElementById('copy-report-btn');

  let currentRawReport = '';

  // Chip click
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      queryInput.value = chip.getAttribute('data-query');
      queryInput.focus();
    });
  });

  // Extract hostname domain from URL
  function extractDomain(urlString) {
    try {
      const u = new URL(urlString);
      return u.hostname.replace('www.', '');
    } catch {
      return 'web';
    }
  }

  // Render markdown with Marked.js cleanly without [1], [2] citation brackets
  function formatStructuredReport(markdownText) {
    if (!markdownText) return '';
    // Strip out all inline [1], [2], [Source 1], [ID] bracketed citation markers from output text
    const cleanText = markdownText
      .replace(/\[\s*(?:source\s*)?\d+(?:\s*,\s*\d+)*\s*\]/gi, '')
      .replace(/\[ID\]/gi, '')
      .replace(/\[\d+(?:-\d+)?\]/g, '')
      .replace(/ {2,}/g, ' ');
    currentRawReport = cleanText;

    // Use marked if available, otherwise simple fallback
    let rawHtml = '';
    if (typeof marked !== 'undefined') {
      rawHtml = marked.parse(cleanText);
    } else {
      rawHtml = cleanText
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br/><br/>');
    }

    return rawHtml;
  }

  // Render rich resource cards in grid
  function renderResourcesGrid(sources) {
    resourcesGrid.innerHTML = '';
    const count = sources ? sources.length : 0;
    resourcesPill.textContent = `${count} Sources`;
    metaSourcesCount.textContent = `${count} Sources`;

    if (!sources || sources.length === 0) {
      resourcesGrid.innerHTML = '<p style="color:var(--text-muted); font-size:0.9rem; grid-column:1/-1;">No external sources were recorded for this query.</p>';
      return;
    }

    sources.forEach(src => {
      const domain = extractDomain(src.url);
      const isTavily = src.tool_origin === 'tavily_search';
      const toolLabel = isTavily ? 'Tavily Search' : 'Wikipedia';
      const toolClass = isTavily ? 'tavily' : 'wikipedia';

      const card = document.createElement('div');
      card.className = 'resource-card';
      card.id = `res-${src.id}`;

      card.innerHTML = `
        <div class="resource-top">
          <div class="resource-tags">
            <span class="domain-pill" style="font-weight:600; color:var(--accent-cyan);">Source ${src.id}</span>
            <div style="display:flex; gap:6px; align-items:center;">
              <span class="domain-pill" title="${domain}">${domain}</span>
              <span class="tool-badge ${toolClass}">${toolLabel}</span>
            </div>
          </div>
          <a href="${src.url}" target="_blank" rel="noopener noreferrer" class="resource-title" title="${src.title}">
            ${src.title}
          </a>
          <div class="resource-snippet">
            "${src.snippet ? src.snippet.trim() : 'No snippet excerpt available.'}"
          </div>
        </div>
        <div class="resource-footer">
          <a href="${src.url}" target="_blank" rel="noopener noreferrer" class="btn-link-action">
            <span>Open Source</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </a>
          <button type="button" class="btn-link-action copy-url-btn" data-url="${src.url}">
            <span>Copy Link</span>
          </button>
        </div>
      `;

      resourcesGrid.appendChild(card);
    });

    // Wire up copy link buttons
    resourcesGrid.querySelectorAll('.copy-url-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const url = btn.getAttribute('data-url');
        navigator.clipboard.writeText(url).then(() => {
          const original = btn.querySelector('span').textContent;
          btn.querySelector('span').textContent = 'Copied!';
          setTimeout(() => { btn.querySelector('span').textContent = original; }, 1500);
        });
      });
    });

    // Add click listeners to report citation badges for smooth scroll and highlight
    reportContent.querySelectorAll('.citation-badge').forEach(badge => {
      badge.addEventListener('click', (e) => {
        e.preventDefault();
        const id = badge.getAttribute('data-id');
        const targetCard = document.getElementById(`res-${id}`);
        if (targetCard) {
          targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetCard.classList.remove('highlight');
          void targetCard.offsetWidth; // Trigger reflow for re-animation
          targetCard.classList.add('highlight');
        }
      });
    });
  }

  // Copy Full Markdown Report
  copyReportBtn.addEventListener('click', () => {
    if (!currentRawReport) return;
    navigator.clipboard.writeText(currentRawReport).then(() => {
      const span = copyReportBtn.querySelector('span');
      const orig = span.textContent;
      span.textContent = 'Report Copied!';
      setTimeout(() => { span.textContent = orig; }, 2000);
    });
  });

  // Handle Form Submission with SSE Streaming
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    const maxSteps = 2;

    // Reset UI state
    submitBtn.disabled = true;
    submitBtn.querySelector('span').textContent = 'Investigating...';
    timeline.innerHTML = '';
    progressSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    stepBadge.textContent = `Iteration 0 of ${maxSteps}`;

    try {
      const streamUrl = `/api/research/stream?query=${encodeURIComponent(query)}&max_steps=${maxSteps}`;
      const eventSource = new EventSource(streamUrl);

      eventSource.addEventListener('start', (e) => {
        const data = JSON.parse(e.data);
        stepBadge.textContent = `Starting Iteration 1 of ${data.max_steps}`;
      });

      eventSource.addEventListener('step', (e) => {
        const data = JSON.parse(e.data);
        stepBadge.textContent = `Iteration ${data.step} of ${maxSteps}`;

        const stepEl = document.createElement('div');
        stepEl.className = 'timeline-step';
        stepEl.id = `step-node-${data.step}`;

        let argsSnippet = JSON.stringify(data.args);
        if (argsSnippet.length > 90) argsSnippet = argsSnippet.substring(0, 90) + '...';

        stepEl.innerHTML = `
          <div class="step-meta">
            <span class="tool-tag">${data.tool_name}</span>
            <span class="step-time">Iteration ${data.step}</span>
          </div>
          <div class="step-details">
            <div>Executing autonomous retrieval:</div>
            <div class="step-args">${argsSnippet}</div>
            <div class="obs-container" id="obs-${data.step}">
              <div class="spinner" style="margin-top:8px; width:14px; height:14px;"></div>
            </div>
          </div>
        `;
        timeline.appendChild(stepEl);
        stepEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });

      eventSource.addEventListener('observation', (e) => {
        const data = JSON.parse(e.data);
        const obsContainer = document.getElementById(`obs-${data.step}`);
        const stepNode = document.getElementById(`step-node-${data.step}`);

        if (stepNode) {
          stepNode.classList.add(data.status === 'success' ? 'success' : 'warning');
        }

        if (obsContainer) {
          if (data.sources && data.sources.length > 0) {
            let listHtml = '<ul class="step-obs-list">';
            data.sources.forEach(s => {
              const domain = extractDomain(s.url);
              listHtml += `
                <li class="step-obs-item">
                  <span class="citation-badge">Source ${s.citation_id || s.id}</span>
                  <span>${s.title}</span>
                  <span class="domain-pill">${domain}</span>
                </li>
              `;
            });
            listHtml += '</ul>';
            obsContainer.innerHTML = listHtml;
          } else {
            obsContainer.innerHTML = `<div style="margin-top:6px; color:var(--text-muted); font-size:0.85rem;">${data.message || 'Observation processed.'}</div>`;
          }
        }
      });



      eventSource.addEventListener('complete', (e) => {
        const data = JSON.parse(e.data);
        eventSource.close();

        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Investigate';
        stepBadge.textContent = 'Mission Complete';

        // Render Markdown structured report
        reportContent.innerHTML = formatStructuredReport(data.final_report);

        // Render audit badge
        if (data.audit && data.audit.all_valid) {
          auditBadge.textContent = '100% Verified Citations';
          auditBadge.style.color = 'var(--accent-emerald)';
        } else {
          auditBadge.textContent = 'General Synthesis';
          auditBadge.style.color = 'var(--accent-amber)';
        }

        // Render rich resources grid
        renderResourcesGrid(data.sources);

        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
      });

      eventSource.addEventListener('error_event', (e) => {
        const data = JSON.parse(e.data);
        eventSource.close();
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Investigate';
        stepBadge.textContent = 'API Notice';

        const errEl = document.createElement('div');
        errEl.className = 'timeline-step warning';
        errEl.innerHTML = `
          <div class="step-meta">
            <span class="tool-tag" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border-color: rgba(239, 68, 68, 0.3);">Error</span>
            <span class="step-time">Notice</span>
          </div>
          <div class="step-details">
            <div style="color: #f87171; font-weight:600;">Research Failed</div>
            <div style="margin-top:6px; color: var(--text-secondary); font-size:0.9rem; word-break: break-word;">
              ${data.message || 'An error occurred during autonomous research.'}
            </div>
          </div>
        `;
        timeline.appendChild(errEl);
        errEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });

      eventSource.onerror = () => {
        eventSource.close();
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Investigate';
      };

    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.querySelector('span').textContent = 'Investigate';
      console.error('Submission error:', err);
    }
  });
});
