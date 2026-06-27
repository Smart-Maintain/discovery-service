import os
import json
import requests

def parse_semgrep():
    try:
        with open('semgrep-results.json', 'r') as f:
            data = json.load(f)
            return len(data.get('results', []))
    except Exception:
        return "Erreur de lecture"

def parse_snyk():
    try:
        with open('snyk-results.json', 'r') as f:
            data = json.load(f)
            # Snyk peut retourner un dictionnaire unique ou une liste de dictionnaires
            if isinstance(data, list):
                return sum(len(repo.get('vulnerabilities', [])) for repo in data)
            return len(data.get('vulnerabilities', []))
    except Exception:
        return "Erreur de lecture"

def parse_trivy():
    try:
        with open('trivy-results.json', 'r') as f:
            data = json.load(f)
            vulns = 0
            for result in data.get('Results', []):
                vulns += len(result.get('Vulnerabilities', []))
            return vulns
    except Exception:
        return "Erreur de lecture"

def send_telegram_message(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print("Erreur : Tokens Telegram manquants dans l'environnement.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Notification Telegram envoyée avec succès !")
        else:
            print(f"Échec de l'envoi Telegram : {response.text}")
    except Exception as e:
        print(f"Erreur lors de l'envoi Telegram : {e}")

if __name__ == "__main__":
    semgrep_vulns = parse_semgrep()
    snyk_vulns = parse_snyk()
    trivy_vulns = parse_trivy()

    msg = (
        "🛡️ *Rapport de Sécurité DevSecOps*\n"
        "📌 *Projet :* `discovery-service-aerospace`\n\n"
        f"🔍 *Semgrep (SAST) :* `{semgrep_vulns}` vulnérabilité(s) trouvée(s)\n"
        f"📦 *Snyk (SCA) :* `{snyk_vulns}` vulnérabilité(s) détectée(s)\n"
        f"🐳 *Trivy (Fichiers) :* `{trivy_vulns}` vulnérabilité(s) détectée(s)\n\n"
        "🚀 _Pipeline exécuté avec succès en mode scan local (Docker bypassé)._"
    )
    
    print(msg)
    send_telegram_message(msg)
