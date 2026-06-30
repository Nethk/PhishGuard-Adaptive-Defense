// background.js

//A helper function to get the URL saved from storage when starting
function getApiUrl(callback) {
    chrome.storage.local.get(['pg_server_url'], (res) => {
        // If there is no saved one, take the default one.
        const url = res.pg_server_url || "https://7d5d-111-223-183-153.ngrok-free.app";
        callback(url);
    });
}

chrome.runtime.onInstalled.addListener(() => {
    getApiUrl((apiUrl) => {
        fetch(apiUrl + '/api/get_current_user')
            .then(r => r.json())
            .then(data => {
                if(data.user_id) {
                    chrome.storage.local.set({'pg_user_id': data.user_id});
                    console.log("🛡️ ID Fetched directly from server: " + data.user_id);
                }
            })
            .catch(e => console.log("Backend Offline on Install"));
    });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        
        
        if (tab.url.includes('127.0.0.1') || tab.url.includes('ngrok-free.app')) return;

        getApiUrl((apiUrl) => {
            chrome.storage.local.get(['pg_user_id'], function(res) {
                const uId = res.pg_user_id;
                if (!uId) return;

                fetch(`${apiUrl}/api/inspect_url?url=${encodeURIComponent(tab.url)}&user_id=${uId}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.is_suspicious) {
                            chrome.tabs.sendMessage(tabId, {
                                action: "PHISHING_DETECTED",
                                reasons: data.reasons
                            });
                        }
                    }).catch(e => console.log("Backend Offline"));
            });
        });
    }
});