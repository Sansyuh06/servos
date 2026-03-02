/* ═══════════════════════════════════════════════════════════
   Servos – Frontend Application Logic
   Single-Page App with API integration
   ═══════════════════════════════════════════════════════════ */

const API = '';
let currentPage = 'dashboard';
let selectedDevice = null;
let selectedMode = 'full_auto';

// ── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    navigate('dashboard');
    checkLLMStatus();
});

function navigate(page) {
    currentPage = page;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const active = document.querySelector(`[data-page="${page}"]`);
    if (active) active.classList.add('active');

    const main = document.getElementById('mainContent');
    main.scrollTop = 0;

    switch (page) {
        case 'dashboard': renderDashboard(); break;
        case 'investigate': renderInvestigate(); break;
        case 'scan': renderScan(); break;
        case 'cases': renderCases(); break;
        case 'playbooks': renderPlaybooks(); break;
        case 'settings': renderSettings(); break;
        default: renderDashboard();
    }
}

async function api(path, opts = {}) {
    const res = await fetch(API + path, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
        body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

async function checkLLMStatus() {
    try {
        const data = await api('/api/llm/status');
        const el = document.getElementById('llmStatus');
        if (data.available) {
            el.innerHTML = `<span class="status-dot online"></span><span>LLM: ${data.model}</span>`;
        } else {
            el.innerHTML = `<span class="status-dot offline"></span><span>LLM: Offline (fallback)</span>`;
        }
    } catch { }
}

// ── Dashboard ───────────────────────────────────────────────
async function renderDashboard() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Overview of your forensic investigations</p>
        </div>
        <div class="stats-grid" id="dashStats"></div>
        <div class="grid-2 mb-24">
            <div class="card stagger-2" id="recentCases">
                <div class="card-title">📁 Recent Cases</div>
                <div class="empty-state"><div class="spinner"></div>Loading...</div>
            </div>
            <div class="card stagger-3" id="dashDevices">
                <div class="card-title">💾 Connected Devices</div>
                <div class="empty-state"><div class="spinner"></div>Loading...</div>
            </div>
        </div>
        <div class="card stagger-4">
            <div class="card-title">🚀 Quick Actions</div>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="navigate('investigate')">🔍 New Investigation</button>
                <button class="btn btn-secondary" onclick="navigate('scan')">⚡ Quick Scan</button>
                <button class="btn btn-secondary" onclick="navigate('cases')">📁 View Cases</button>
                <button class="btn btn-secondary" onclick="navigate('playbooks')">📋 Playbooks</button>
            </div>
        </div>`;

    // Load stats
    try {
        const [devData, caseData] = await Promise.all([api('/api/devices'), api('/api/cases')]);
        const cases = caseData.cases || [];
        document.getElementById('dashStats').innerHTML = `
            <div class="stat-card stagger-1"><div class="stat-icon">📁</div><div class="stat-value">${cases.length}</div><div class="stat-label">Total Cases</div></div>
            <div class="stat-card stagger-2"><div class="stat-icon">💾</div><div class="stat-value">${devData.devices.length}</div><div class="stat-label">Devices Connected</div></div>
            <div class="stat-card stagger-3"><div class="stat-icon">✅</div><div class="stat-value">${cases.filter(c => c.status === 'completed').length}</div><div class="stat-label">Completed</div></div>
            <div class="stat-card stagger-4"><div class="stat-icon">🔴</div><div class="stat-value">${cases.filter(c => c.status === 'active').length}</div><div class="stat-label">Active</div></div>`;

        // Recent cases
        const casesEl = document.getElementById('recentCases');
        if (cases.length === 0) {
            casesEl.innerHTML = `<div class="card-title">📁 Recent Cases</div><div class="empty-state"><div class="icon">📂</div><h3>No cases yet</h3><p>Start your first investigation</p><button class="btn btn-primary btn-sm" onclick="navigate('investigate')">New Investigation</button></div>`;
        } else {
            let rows = cases.slice(0, 5).map(c => `<tr><td style="color:var(--cyan);font-family:var(--font-mono)">${c.id}</td><td>${(c.created_at || '').slice(0, 10)}</td><td><span class="badge badge-${c.status === 'completed' ? 'green' : c.status === 'active' ? 'blue' : 'yellow'}">${c.status}</span></td></tr>`).join('');
            casesEl.innerHTML = `<div class="card-title">📁 Recent Cases</div><div class="table-wrap"><table><thead><tr><th>Case ID</th><th>Date</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table></div>`;
        }

        // Devices
        const devEl = document.getElementById('dashDevices');
        if (devData.devices.length === 0) {
            devEl.innerHTML = `<div class="card-title">💾 Connected Devices</div><div class="empty-state"><div class="icon">💾</div><h3>No devices</h3><p>Connect a USB drive to scan</p></div>`;
        } else {
            let devRows = devData.devices.map(d => `<tr><td style="font-weight:600">${d.name || d.path}</td><td>${d.mount_point}</td><td>${d.filesystem}</td><td>${d.capacity_human || '—'}</td></tr>`).join('');
            devEl.innerHTML = `<div class="card-title">💾 Connected Devices</div><div class="table-wrap"><table><thead><tr><th>Device</th><th>Mount</th><th>FS</th><th>Capacity</th></tr></thead><tbody>${devRows}</tbody></table></div>`;
        }
    } catch (e) {
        document.getElementById('dashStats').innerHTML = `<div class="stat-card"><div class="stat-icon">⚠️</div><div class="stat-value">—</div><div class="stat-label">Error loading data</div></div>`;
    }
}

// ── New Investigation ───────────────────────────────────────
async function renderInvestigate() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">🔍 New Investigation</h1>
            <p class="page-subtitle">Select a device and investigation mode to begin</p>
        </div>
        <div class="card mb-24 stagger-1">
            <div class="card-title">Step 1: Select Target</div>
            <div id="deviceList"><div class="empty-state"><div class="spinner"></div>Detecting devices...</div></div>
            <div class="input-group" style="margin-top:16px">
                <label>Or enter a path manually</label>
                <input class="input" id="manualPath" placeholder="e.g. D:\\ or E:\\SuspiciousUSB">
            </div>
        </div>
        <div class="card mb-24 stagger-2">
            <div class="card-title">Step 2: Investigation Mode</div>
            <div class="mode-grid">
                <div class="mode-card selected" data-mode="full_auto" onclick="selectMode(this,'full_auto')">
                    <div class="mode-icon">🤖</div>
                    <div class="mode-name">Full Automation</div>
                    <div class="mode-desc">Servos handles everything automatically and produces a final report.</div>
                </div>
                <div class="mode-card" data-mode="hybrid" onclick="selectMode(this,'hybrid')">
                    <div class="mode-icon">🤝</div>
                    <div class="mode-name">Hybrid</div>
                    <div class="mode-desc">Step-by-step with your approval at each stage.</div>
                </div>
                <div class="mode-card" data-mode="manual" onclick="selectMode(this,'manual')">
                    <div class="mode-icon">🧑‍💻</div>
                    <div class="mode-name">Manual</div>
                    <div class="mode-desc">Expert mode – guided checklists, you execute.</div>
                </div>
            </div>
        </div>
        <div class="card mb-24 stagger-3">
            <div class="card-title">Step 3: Investigator</div>
            <div class="input-group"><label>Your name</label><input class="input" id="investigatorName" value="Investigator" placeholder="Enter your name"></div>
        </div>
        <div style="text-align:right" class="stagger-4">
            <button class="btn btn-primary btn-lg" onclick="startInvestigation()">🚀 Start Investigation</button>
        </div>`;

    try {
        const data = await api('/api/devices');
        const el = document.getElementById('deviceList');
        if (data.devices.length === 0) {
            el.innerHTML = `<p style="color:var(--text-muted)">No devices detected. Enter a path manually below.</p>`;
        } else {
            el.innerHTML = `<div class="device-grid">${data.devices.map((d, i) => `
                <div class="device-card" onclick="selectDevice(this, ${i})" data-idx="${i}" data-path="${d.path}" data-mount="${d.mount_point}" data-name="${d.name || d.path}">
                    <div class="device-icon">${d.is_removable ? '🔌' : '💾'}</div>
                    <div class="device-name">${d.name || d.path}</div>
                    <div class="device-path">${d.mount_point}</div>
                    <div class="device-meta"><span>${d.filesystem}</span><span>${d.capacity_human || '—'}</span>${d.is_removable ? '<span class="badge badge-cyan">Removable</span>' : ''}</div>
                </div>`).join('')}</div>`;
        }
    } catch { }
}

function selectDevice(el, idx) {
    document.querySelectorAll('.device-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    selectedDevice = { path: el.dataset.path, mount: el.dataset.mount, name: el.dataset.name };
}

function selectMode(el, mode) {
    document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    selectedMode = mode;
}

async function startInvestigation() {
    const manual = document.getElementById('manualPath')?.value?.trim();
    const investigator = document.getElementById('investigatorName')?.value || 'Investigator';
    let devPath, mountPoint, devName;

    if (manual) {
        devPath = manual; mountPoint = manual; devName = manual;
    } else if (selectedDevice) {
        devPath = selectedDevice.path; mountPoint = selectedDevice.mount; devName = selectedDevice.name;
    } else {
        alert('Please select a device or enter a path.');
        return;
    }

    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="investigation-panel fade-in">
            <div class="spinner"></div>
            <h2>Investigation Starting...</h2>
            <div class="investigation-step" id="invStep">Initializing...</div>
            <div class="progress-bar"><div class="progress-fill" id="invProgress" style="width:0%"></div></div>
            <div class="progress-label"><span id="invPercent">0%</span><span id="invStatus">Starting...</span></div>
        </div>
        <div id="invResults"></div>`;

    try {
        const res = await api('/api/investigate', {
            method: 'POST',
            body: { device_path: devPath, mount_point: mountPoint, device_name: devName, mode: selectedMode, investigator }
        });
        pollInvestigation(res.case_id);
    } catch (e) {
        document.getElementById('invStep').textContent = `Error: ${e.message}`;
    }
}

async function pollInvestigation(caseId) {
    const poll = async () => {
        try {
            const s = await api(`/api/investigate/${caseId}/status`);
            document.getElementById('invStep').textContent = s.step;
            document.getElementById('invProgress').style.width = s.progress + '%';
            document.getElementById('invPercent').textContent = s.progress + '%';
            document.getElementById('invStatus').textContent = s.status;

            if (s.status === 'completed') {
                renderResults(s.result, caseId);
                return;
            } else if (s.status === 'error') {
                document.getElementById('invStep').textContent = '❌ ' + s.step;
                document.getElementById('invStep').style.color = 'var(--red)';
                return;
            }
            setTimeout(poll, 1000);
        } catch { setTimeout(poll, 2000); }
    };
    setTimeout(poll, 1500);
}

function renderResults(result, caseId) {
    const panel = document.querySelector('.investigation-panel');
    const risk = result?.findings?.malware?.risk_level || result?.interpretation?.risk || 'UNKNOWN';
    panel.innerHTML = `
        <h2 style="color:var(--green)">✅ Investigation Complete</h2>
        <p style="color:var(--text-secondary);margin-top:8px">Case ID: <span style="color:var(--cyan);font-family:var(--font-mono)">${result.id}</span></p>
        <div class="risk-display">
            <div class="risk-circle risk-${risk}">${risk}</div>
        </div>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:16px;">
            <a href="/api/reports/${caseId}/txt" class="btn btn-primary btn-sm" target="_blank">📄 TXT Report</a>
            <a href="/api/reports/${caseId}/json" class="btn btn-secondary btn-sm" target="_blank">📋 JSON</a>
            <a href="/api/reports/${caseId}/pdf" class="btn btn-secondary btn-sm" target="_blank">📕 PDF</a>
            <button class="btn btn-secondary btn-sm" onclick="navigate('dashboard')">← Dashboard</button>
        </div>`;

    const resultsEl = document.getElementById('invResults');
    let html = '<div class="results-section fade-in">';

    // AI Summary
    if (result.interpretation) {
        html += `<div class="card mb-24"><div class="card-title">🤖 AI Analysis</div><p style="color:var(--text-secondary);line-height:1.7">${result.interpretation.summary || 'No summary available.'}</p>`;
        if (result.interpretation.recommendations?.length) {
            html += '<div style="margin-top:16px"><strong>Recommendations:</strong><ul style="margin-top:8px;padding-left:20px">';
            result.interpretation.recommendations.forEach(r => { html += `<li style="color:var(--text-secondary);margin-bottom:6px">${r}</li>`; });
            html += '</ul></div>';
        }
        html += '</div>';
    }

    // File Stats
    if (result.findings?.file_system) {
        const fs = result.findings.file_system;
        html += `<div class="card mb-24"><div class="card-title">📂 File System</div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-value">${fs.total_files || 0}</div><div class="stat-label">Total Files</div></div>
                <div class="stat-card"><div class="stat-value">${fs.suspicious || 0}</div><div class="stat-label">Suspicious</div></div>
            </div>`;
        if (fs.types) {
            const entries = Object.entries(fs.types).slice(0, 8);
            const maxVal = Math.max(...entries.map(e => e[1]));
            html += '<div class="chart-bar-wrap" style="margin-top:16px">';
            entries.forEach(([ext, count]) => {
                const pct = Math.max(5, (count / maxVal) * 100);
                html += `<div class="chart-bar-item"><span class="chart-bar-label">${ext}</span><div class="chart-bar"><div class="chart-bar-fill" style="width:${pct}%">${count}</div></div></div>`;
            });
            html += '</div>';
        }
        html += '</div>';
    }

    // Suspicious files
    if (result.findings?.suspicious_files?.length) {
        html += `<div class="card mb-24"><div class="card-title">⚠️ Suspicious Files (${result.findings.suspicious_files.length})</div><div class="table-wrap"><table><thead><tr><th>File</th><th>Reason</th><th>Entropy</th></tr></thead><tbody>`;
        result.findings.suspicious_files.forEach(f => {
            html += `<tr><td style="font-family:var(--font-mono);color:var(--orange)">${f.name}</td><td style="color:var(--text-secondary)">${f.reason}</td><td>${(f.entropy || 0).toFixed(2)}</td></tr>`;
        });
        html += '</tbody></table></div></div>';
    }

    // Malware indicators
    if (result.findings?.malware_indicators?.length) {
        html += `<div class="card mb-24"><div class="card-title">🦠 Malware Indicators</div>`;
        result.findings.malware_indicators.forEach(ind => {
            html += `<div class="indicator-item ${ind.severity}">
                <span class="indicator-severity" style="color:var(--${ind.severity === 'critical' ? 'red' : ind.severity === 'high' ? 'orange' : ind.severity === 'medium' ? 'yellow' : 'teal'})">${ind.severity}</span>
                <div><strong>${ind.rule}</strong><br><span style="color:var(--text-muted)">${ind.file} – ${ind.description}</span></div></div>`;
        });
        html += '</div>';
    }

    // Timeline
    if (result.findings?.timeline_events?.length) {
        html += `<div class="card mb-24"><div class="card-title">📅 Activity Timeline</div><div class="timeline">`;
        result.findings.timeline_events.slice(0, 25).forEach(ev => {
            html += `<div class="timeline-item ${ev.severity}"><div class="timeline-time">${ev.timestamp}</div><div class="timeline-desc">${ev.description}</div></div>`;
        });
        html += '</div></div>';
    }

    // Backup info
    if (result.backup) {
        html += `<div class="card mb-24"><div class="card-title">🔒 Chain of Custody</div>
            <div class="setting-row"><span class="setting-key">Backup Path</span><span class="setting-value">${result.backup.backup_path}</span></div>
            <div class="setting-row"><span class="setting-key">Files Backed Up</span><span class="setting-value">${result.backup.files_backed_up}</span></div>
            <div class="setting-row"><span class="setting-key">MD5</span><span class="setting-value" style="font-size:11px">${result.backup.hash_md5}</span></div>
            <div class="setting-row"><span class="setting-key">SHA-256</span><span class="setting-value" style="font-size:11px">${result.backup.hash_sha256}</span></div>
        </div>`;
    }

    html += '</div>';
    resultsEl.innerHTML = html;
}

// ── Quick Scan ──────────────────────────────────────────────
function renderScan() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">⚡ Quick Scan</h1>
            <p class="page-subtitle">Scan any directory for suspicious files and malware indicators</p>
        </div>
        <div class="card mb-24 stagger-1">
            <div class="input-group"><label>Target Path</label><input class="input" id="scanPath" placeholder="Enter directory path to scan, e.g. D:\\"></div>
            <button class="btn btn-primary" onclick="runScan()">⚡ Scan Now</button>
        </div>
        <div id="scanResults"></div>`;
}

async function runScan() {
    const path = document.getElementById('scanPath')?.value?.trim();
    if (!path) { alert('Enter a path.'); return; }

    const el = document.getElementById('scanResults');
    el.innerHTML = `<div class="card"><div class="spinner"></div><p style="text-align:center;color:var(--text-muted)">Scanning ${path}...</p></div>`;

    try {
        const r = await api('/api/scan', { method: 'POST', body: { target_path: path } });
        let html = `<div class="stats-grid mb-24 fade-in">
            <div class="stat-card"><div class="stat-icon">📄</div><div class="stat-value">${r.total_files}</div><div class="stat-label">Files Found</div></div>
            <div class="stat-card"><div class="stat-icon">📁</div><div class="stat-value">${r.total_dirs}</div><div class="stat-label">Directories</div></div>
            <div class="stat-card"><div class="stat-icon">⚠️</div><div class="stat-value">${r.suspicious_files.length}</div><div class="stat-label">Suspicious</div></div>
            <div class="stat-card"><div class="stat-icon">🛡️</div><div class="stat-value"><span style="color:var(--${r.malware.risk_level === 'LOW' ? 'green' : r.malware.risk_level === 'MEDIUM' ? 'yellow' : 'red'})">${r.malware.risk_level}</span></div><div class="stat-label">Risk Level</div></div>
        </div>`;

        if (r.file_types && Object.keys(r.file_types).length) {
            const entries = Object.entries(r.file_types).slice(0, 10);
            const mx = Math.max(...entries.map(e => e[1]));
            html += '<div class="card mb-24 fade-in"><div class="card-title">📊 File Types</div><div class="chart-bar-wrap">';
            entries.forEach(([ext, cnt]) => {
                html += `<div class="chart-bar-item"><span class="chart-bar-label">${ext}</span><div class="chart-bar"><div class="chart-bar-fill" style="width:${Math.max(5, (cnt / mx) * 100)}%">${cnt}</div></div></div>`;
            });
            html += '</div></div>';
        }

        if (r.suspicious_files.length) {
            html += `<div class="card mb-24 fade-in"><div class="card-title">⚠️ Suspicious Files</div><div class="table-wrap"><table><thead><tr><th>File</th><th>Reason</th><th>Entropy</th></tr></thead><tbody>`;
            r.suspicious_files.forEach(f => {
                html += `<tr><td style="color:var(--orange);font-family:var(--font-mono)">${f.name}</td><td style="color:var(--text-secondary)">${f.reason}</td><td>${(f.entropy || 0).toFixed(2)}</td></tr>`;
            });
            html += '</tbody></table></div></div>';
        }

        if (r.malware.indicators.length) {
            html += `<div class="card fade-in"><div class="card-title">🦠 Malware Indicators</div>`;
            r.malware.indicators.forEach(ind => {
                html += `<div class="indicator-item ${ind.severity}"><span class="indicator-severity">${ind.severity.toUpperCase()}</span><div><strong>${ind.rule}</strong> – ${ind.description}<br><span style="color:var(--text-muted);font-size:12px">${ind.file}</span></div></div>`;
            });
            html += '</div>';
        }

        el.innerHTML = html;
    } catch (e) {
        el.innerHTML = `<div class="card"><p style="color:var(--red)">❌ Error: ${e.message}</p></div>`;
    }
}

// ── Cases ───────────────────────────────────────────────────
async function renderCases() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">📁 Past Cases</h1>
            <p class="page-subtitle">View and manage your investigations</p>
        </div>
        <div class="card stagger-1" id="casesList"><div class="spinner"></div></div>`;

    try {
        const data = await api('/api/cases');
        const el = document.getElementById('casesList');
        if (!data.cases.length) {
            el.innerHTML = `<div class="empty-state"><div class="icon">📂</div><h3>No cases yet</h3><p>Start your first investigation to see it here</p><button class="btn btn-primary" onclick="navigate('investigate')">New Investigation</button></div>`;
        } else {
            let rows = data.cases.map(c => {
                const dev = c.device_info || {};
                return `<tr>
                    <td style="color:var(--cyan);font-family:var(--font-mono)">${c.id}</td>
                    <td>${(c.created_at || '').slice(0, 19)}</td>
                    <td>${dev.name || dev.path || '—'}</td>
                    <td><span class="badge badge-blue">${c.mode}</span></td>
                    <td><span class="badge badge-${c.status === 'completed' ? 'green' : c.status === 'active' ? 'blue' : 'yellow'}">${c.status}</span></td>
                    <td>${c.report_path ? `<a href="/api/reports/${c.id}/txt" target="_blank" class="btn btn-sm btn-secondary">📄</a>` : '—'}</td>
                </tr>`;
            }).join('');
            el.innerHTML = `<div class="card-title">📁 All Cases (${data.cases.length})</div><div class="table-wrap"><table><thead><tr><th>Case ID</th><th>Date</th><th>Device</th><th>Mode</th><th>Status</th><th>Report</th></tr></thead><tbody>${rows}</tbody></table></div>`;
        }
    } catch (e) {
        document.getElementById('casesList').innerHTML = `<p style="color:var(--red)">Error: ${e.message}</p>`;
    }
}

// ── Playbooks ───────────────────────────────────────────────
async function renderPlaybooks() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">📋 Investigation Playbooks</h1>
            <p class="page-subtitle">Reusable investigation workflows</p>
        </div>
        <div id="playbookList" class="stagger-1"><div class="spinner"></div></div>`;

    try {
        const data = await api('/api/playbooks');
        const el = document.getElementById('playbookList');
        if (!data.playbooks.length) {
            el.innerHTML = `<div class="empty-state"><div class="icon">📋</div><h3>No playbooks</h3></div>`;
        } else {
            el.innerHTML = data.playbooks.map(pb => `
                <div class="playbook-card mb-16">
                    <div class="playbook-name">📋 ${pb.name}</div>
                    <div class="playbook-desc">${pb.description}</div>
                    <div class="playbook-meta">
                        <span>${pb.steps} steps</span>
                        <span>v${pb.version}</span>
                        ${pb.metadata?.difficulty ? `<span class="badge badge-blue">${pb.metadata.difficulty}</span>` : ''}
                        ${pb.metadata?.estimated_duration_minutes ? `<span>~${pb.metadata.estimated_duration_minutes} min</span>` : ''}
                    </div>
                </div>`).join('');
        }
    } catch { }
}

// ── Settings ────────────────────────────────────────────────
async function renderSettings() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="page-header fade-in">
            <h1 class="page-title">⚙️ Settings</h1>
            <p class="page-subtitle">Configure Servos</p>
        </div>
        <div class="card stagger-1" id="settingsPanel"><div class="spinner"></div></div>`;

    try {
        const data = await api('/api/settings');
        const s = data.settings;
        const groups = {
            'LLM Configuration': ['llm_model', 'llm_base_url', 'llm_timeout', 'llm_enabled'],
            'Storage & Paths': ['backup_location', 'reports_dir', 'data_dir', 'database_path'],
            'Analysis': ['entropy_threshold', 'max_file_size_mb', 'scan_hidden_files', 'hash_algorithms'],
            'Detection': ['usb_poll_interval', 'auto_detect_usb'],
        };

        let html = '';
        for (const [group, keys] of Object.entries(groups)) {
            html += `<div class="settings-group"><h3>${group}</h3>`;
            keys.forEach(k => {
                if (s[k] !== undefined) {
                    html += `<div class="setting-row"><span class="setting-key">${k}</span><span class="setting-value">${JSON.stringify(s[k])}</span></div>`;
                }
            });
            html += '</div>';
        }
        document.getElementById('settingsPanel').innerHTML = `<div class="card-title">⚙️ Configuration</div>${html}`;
    } catch { }
}
