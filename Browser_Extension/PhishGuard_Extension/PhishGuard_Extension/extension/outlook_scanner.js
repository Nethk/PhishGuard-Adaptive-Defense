function scanOutlookContent() {
    // The general class of the email body in Outlook
    const emailBodyElement = document.querySelector('[aria-label="Message body"]');
    // To capture the sender
    const senderElement = document.querySelector('span[title*="@"]');

    if (!emailBodyElement || !senderElement) return;

    const emailBody = emailBodyElement.innerText;
    const sender = senderElement.getAttribute('title');

    fetch('https://7d5d-111-223-183-153.ngrok-free.app/api/inspect_email', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ body: emailBody, sender: sender })
    })
    .then(r => r.json())
    .then(data => {
        if (data.is_phishing) {
            showChallengeBox(data.reasons, "OUTLOOK_SCAN");
        }
    });
}

// Outlook MutationObserver
const outlookObserver = new MutationObserver(scanOutlookContent);
outlookObserver.observe(document.body, { childList: true, subtree: true });