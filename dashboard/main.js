const GITHUB_REPO = 'zaid-117-cmyk/client-previews';
const GITHUB_API_URL = `https://api.github.com/repos/${GITHUB_REPO}/contents/previews`;
const LOCAL_DATA_URL = '/data/campaign_log.json';

// Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Generate Slug
function generateSlug(companyName) {
    return companyName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

// Fetch Campaign Data
async function fetchData() {
    const btn = document.getElementById('refresh-btn');
    if(btn) btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Refreshing...`;

    try {
        let sentLogs = [];
        try {
            const localRes = await fetch(LOCAL_DATA_URL);
            if(localRes.ok) sentLogs = await localRes.json();
        } catch(e) {}

        let generatedSlugs = [];
        try {
            const githubRes = await fetch(GITHUB_API_URL);
            if(githubRes.ok) {
                const contents = await githubRes.json();
                generatedSlugs = contents.filter(item => item.type === 'dir').map(dir => dir.name);
            }
        } catch(e) {}

        // Fetch scores in parallel
        const scores = {};
        await Promise.all(generatedSlugs.map(async (slug) => {
            try {
                const rawUrl = `https://raw.githubusercontent.com/${GITHUB_REPO}/main/previews/${slug}/score.json`;
                const res = await fetch(rawUrl);
                if(res.ok) {
                    const data = await res.json();
                    scores[slug] = data.score || "WARM";
                } else {
                    scores[slug] = "WARM";
                }
            } catch(e) { scores[slug] = "WARM"; }
        }));

        updateUI(sentLogs, generatedSlugs, scores);
    } catch (err) {
        console.error("Dashboard Error:", err);
    }

    if(btn) setTimeout(() => { btn.innerHTML = `<i class="fa-solid fa-rotate"></i> Refresh Data`; }, 500);
}

function updateUI(sentLogs, generatedSlugs, scores) {
    const tbody = document.querySelector('#leads-table tbody');
    tbody.innerHTML = '';

    let totalSent = sentLogs.length;
    let totalReplied = 0;

    const enhancedLogs = sentLogs.map(log => {
        const expectedSlug = generateSlug(log.company);
        const isConverted = generatedSlugs.includes(expectedSlug);
        if (isConverted) totalReplied++;
        return { ...log, isConverted, expectedSlug, score: scores[expectedSlug] };
    });

    document.getElementById('total-sent').innerText = totalSent;
    document.getElementById('total-replied').innerText = totalReplied;
    const rate = totalSent > 0 ? ((totalReplied / totalSent) * 100).toFixed(1) : 0;
    document.getElementById('conversion-rate').innerText = `${rate}%`;

    enhancedLogs.sort((a,b) => (b.isConverted === a.isConverted) ? 0 : a.isConverted ? 1 : -1).forEach(log => {
        const tr = document.createElement('tr');
        
        let statusHtml = log.isConverted 
            ? `<span class="status-badge status-converted"><i class="fa-solid fa-check"></i> Site Generated</span>`
            : `<span class="status-badge status-sent">Emailed</span>`;
            
        let actionHtml = log.isConverted
            ? `<a href="https://elevateweb.me/client-previews/previews/${log.expectedSlug}/" target="_blank" class="action-link" style="margin-right:1rem;">Preview <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
               <a href="javascript:void(0)" onclick="openChat('${log.email}')" class="action-link"><i class="fa-solid fa-message"></i> Chat</a>`
            : `-`;
            
        let scoreHtml = log.isConverted && log.score 
            ? `<span class="score-badge score-${log.score.toLowerCase()}">${log.score}</span>`
            : `<span style="color:var(--text-muted)">-</span>`;

        let dateStr = log.sent_at;
        if(dateStr && dateStr !== "N/A") {
            try { dateStr = new Date(dateStr).toLocaleString(); } catch(e){}
        }

        tr.innerHTML = `
            <td><strong>${log.company}</strong></td>
            <td>${log.first_name} <br><small style="color:var(--text-muted)">${log.email}</small></td>
            <td>${dateStr || '-'}</td>
            <td>${statusHtml}</td>
            <td>${scoreHtml}</td>
            <td>${actionHtml}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Modal Logic
function openChat(email) {
    document.getElementById('chat-modal').style.display = 'flex';
    document.getElementById('chat-title').innerText = `Chat with ${email}`;
    document.getElementById('chat-body').innerHTML = '<div style="text-align:center; padding:2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><br><br>Fetching IMAP History...</div>';
    
    fetch(`/api/chat_history?email=${encodeURIComponent(email)}`)
        .then(res => res.json())
        .then(data => {
            const body = document.getElementById('chat-body');
            body.innerHTML = '';
            if(data.error) {
                body.innerHTML = `<div style="color:#ff4757">Error: ${data.error}</div>`;
                return;
            }
            if(data.messages.length === 0) {
                body.innerHTML = `<div style="color:var(--text-muted)">No chat history found.</div>`;
                return;
            }
            data.messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = 'chat-bubble ' + (msg.is_me ? 'chat-me' : 'chat-client');
                div.innerHTML = `<strong>${msg.subject}</strong><br><br>${msg.body}`;
                body.appendChild(div);
            });
            body.scrollTop = body.scrollHeight;
        })
        .catch(err => {
            document.getElementById('chat-body').innerHTML = `<div style="color:#ff4757">Connection Error</div>`;
        });
}

function closeChat() {
    document.getElementById('chat-modal').style.display = 'none';
}

// Prospector Logic
async function generateProspects() {
    const btn = document.getElementById('generate-prospects-btn');
    const resDiv = document.getElementById('prospector-results');
    const niche = document.getElementById('niche-input').value;
    const city = document.getElementById('city-input').value;

    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating AI Queries...`;
    resDiv.style.display = 'none';

    try {
        const res = await fetch('/api/prospector', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ niche, city })
        });
        const data = await res.json();
        
        resDiv.style.display = 'block';
        if(data.error) {
            resDiv.innerHTML = `<span style="color:#ff4757">Error: ${data.error}</span>`;
        } else {
            resDiv.innerHTML = marked.parse(data.result);
        }
    } catch(e) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = `<span style="color:#ff4757">Failed to connect to server.</span>`;
    }
    
    btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Queries`;
}

// Initial load
fetchData();
