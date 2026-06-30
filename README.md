# PhishGuard: Human-Centric Adaptive Phishing Defense 🛡️

An adaptive cybersecurity framework featuring a gamified security awareness training portal and a real-time DOM-intercepting browser extension.

## 📂 Repository Structure
* **/Backend_Server:** Contains the centralized Python (Flask) REST API, SQLite database, and the gamified training web application.
* **/Browser_Extension:** Contains the Manifest V3 Chrome Extension scripts.
* **/Datasets:** Contains anonymized empirical baseline data from the phishing simulation.

## 📊 Data Privacy and Anonymization Note
You might notice that the `Datasets` folder contains files like `anonymized_Baseline_Phishing_Assessment_Stage_1.csv` where email addresses are not visible. 
* **Why?** To adhere to institutional ethical clearance and data protection protocols, all PII (Personally Identifiable Information) such as actual student emails and IP addresses have been removed. 
* **How it works:** Real identities have been replaced with anonymous participant IDs (e.g., `Participant_1`) to ensure participant confidentiality while allowing for statistical analysis of click-through rates (CTR) and susceptibility metrics.

## 🚀 How the System Works
1. **Initial Onboarding:** Users play the gamified PhishGuard training portal (`Backend_Server/templates/`) to establish a baseline vulnerability profile.
2. **Real-time Surveillance:** The Chrome Extension monitors navigation events. If a suspicious link (e.g., typosquatting, HTTP, or high-risk keywords) is detected, `content.js` intercepts the DOM and triggers a high-severity warning.
3. **Adaptive Enforcement:** If the user repeatedly overrides warnings, the `Lockdown Controller` (in `app.py`) updates the database and revokes standard browsing privileges until the user completes remedial gamified missions.

## 🛠️ Setup Instructions
### 1. Starting the Backend
1. Navigate to `Backend_Server`.
2. Run: `pip install flask flask-cors`
3. Run: `python app.py`

### 2. Loading the Extension
1. Go to `chrome://extensions/` in Chrome.
2. Enable **"Developer mode"**.
3. Select **"Load unpacked"** and point to the `Browser_Extension` folder.
