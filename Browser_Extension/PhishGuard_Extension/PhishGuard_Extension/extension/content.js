console.log("🛡️ PhishGuard Adaptive Sentinel Active");

function getApiUrl(callback) {
    chrome.storage.local.get(['pg_server_url'], (res) => {
        const url = res.pg_server_url || "http://127.0.0.1:5000";
        callback(url);
    });
}

// 1. Dashboard ID Sync
getApiUrl((apiUrl) => {
    if (window.location.href.includes('/dashboard')) {
        const userDiv = document.getElementById('pg-active-user');
        if (userDiv) {
            const uId = userDiv.getAttribute('data-id');
            chrome.storage.local.set({ 'pg_user_id': uId });
        }
    }
});

// 2 & 3. Checks
chrome.storage.local.get(['pg_user_id'], (res) => {
    const uId = res.pg_user_id;
    if (!uId) return;

    getApiUrl((apiUrl) => {
        if (window.location.href.includes(apiUrl) || window.location.href.includes('127.0.0.1')) return;

        // Phishing URL Scan
        fetch(`${apiUrl}/api/inspect_url?url=${encodeURIComponent(window.location.href)}&user_id=${uId}`)
        .then(r => r.json())
        .then(data => {
            if (data.is_suspicious) {
                showChallengeBox(data.reasons, uId);
            }
        }).catch(e => console.log("URL Inspect Offline"));

        // Status badge 
        fetch(`${apiUrl}/api/get_adaptive_status?user_id=${uId}`)
        .then(r => r.json())
        .then(data => {
            const div = document.createElement('div');
            
            div.style.cssText = `position:fixed; top:20px; right:20px; z-index:999999; padding:12px 18px; background:${data.color}; color:#0b132b; font-family:sans-serif; font-size:13px; font-weight:bold; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.3);`;
            div.innerText = "PhishGuard: " + data.message;
            document.body.appendChild(div);
        }).catch(e => console.log("Status Check Offline"));
    });
});

// 4. Modal 
function showChallengeBox(reasons, uId) {
    if (document.getElementById('pg-adaptive-modal')) return;
    const modal = document.createElement('div');
    modal.id = "pg-adaptive-modal";
    
    modal.style.cssText = "position:fixed; top:90px; right:20px; width:360px; background:#0b132b; border:2px solid #ff0055; color:white; font-family:sans-serif; z-index:999999; padding:20px; border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,0.7);";
    
    modal.innerHTML = `
        <div style="color:#ff0055; font-size:14px; font-weight:bold; margin-bottom:10px;">🚨 ADAPTIVE PHISHING ALERT</div>
        <div style="margin:10px 0; font-size:12px; color:#e0e0e0; line-height:1.4; background:#162247; padding:10px; border-radius:5px;">
            ${reasons.join('<br>')}
        </div>
        <button id="pg-btn-back" style="background:#48cae4; color:#0b132b; font-weight:bold; border:none; padding:10px; width:100%; border-radius:5px; cursor:pointer; margin-top:8px;">🛡️ Go Back (Safe)</button>
        <button id="pg-btn-proceed" style="background:transparent; color:#ff0055; border:1px solid #ff0055; padding:8px; width:100%; margin-top:8px; border-radius:5px; cursor:pointer;">Proceed Anyway ⚠️</button>
    `;
    document.body.appendChild(modal);

    document.getElementById('pg-btn-back').onclick = () => sendAction('GO_BACK', uId, modal);
    document.getElementById('pg-btn-proceed').onclick = () => sendAction('PROCEED', uId, modal);
}

// 5. Send Action
function sendAction(actionType, uId, modalNode) {
    getApiUrl((apiUrl) => {
        fetch(apiUrl + '/api/handle_adaptive_interception', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: uId, action: actionType })
        })
        .then(r => r.json())
        .then(data => {
            modalNode.remove();
            if (data.status === "LOCKED") {
                alert(data.msg);
                window.location.href = apiUrl + "/dashboard";
            }
        }).catch(e => console.log("Action Send Offline"));
    });
}