// script runs every time a page in Gmail loads.
function scanEmailContent() {
    // Capture the email body in Gmail (Class .a3s is used for the Gmail body))
    const emailBodyElement = document.querySelector('.a3s');
    const senderElement = document.querySelector('.gD');

    if (!emailBodyElement || !senderElement) return;

    const emailBody = emailBodyElement.innerText;
    const sender = senderElement.getAttribute('email');

    // end it to the backend and scan it.
    fetch('https://7d5d-111-223-183-153.ngrok-free.app/api/inspect_email', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ body: emailBody, sender: sender })
    })
    .then(r => r.json())
    .then(data => {
        if (data.is_phishing) {
            // showChallengeBox 
            showChallengeBox(data.reasons, "GMAIL_SCAN");
        }
    });
}

// Scan when you open an email.
const observer = new MutationObserver(scanEmailContent);
observer.observe(document.body, { childList: true, subtree: true });