// If there is a previously saved link, show it.
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get(['pg_server_url'], (res) => {
    if (res.pg_server_url) {
      document.getElementById('serverUrl').value = res.pg_server_url;
    }
  });
});

// Save 
document.getElementById('saveBtn').addEventListener('click', () => {
  let url = document.getElementById('serverUrl').value.trim();


  if (url.endsWith('/')) {
    url = url.slice(0, -1);
  }

  chrome.storage.local.set({ 'pg_server_url': url }, () => {
    const status = document.getElementById('status');
    status.textContent = '✅ URL Saved Successfully!';
    setTimeout(() => { status.textContent = ''; }, 2500);
  });
});