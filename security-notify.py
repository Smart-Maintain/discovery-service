import os
import json
import requests

def parse_semgrep():
    details = []
    try:
        with open('semgrep-results.json', 'r') as f:
            data = json.load(f)
            results = data.get('results', [])
            for r in results[:5]:  # On limite aux 5 premières pour éviter les messages trop longs
                path = r.get('path', 'Fichier inconnu')
                line = r.get('start', {}).get('line', '?')
                message = r.get('extra', {}).get('message', 'Pas de description').split('\n')[0]
                details.append(f"⚠️ `{path}:{line}` -> {message}")
            return len(results), details
    except Exception:
        return "Erreur", ["❌ Impossible de lire le rapport Semgrep"]

def parse_snyk():
    details = []
    try:
        with open('snyk-results.json', 'r') as f:
            data = json.load(f)
            
            # Gestion des différents formats de retour Snyk
            vulns_list = []
            if isinstance(data, list):
                for repo in data:
                    vulns_list.extend(repo.get('vulnerabilities', []))
            else:
                vulns_list = data.get('vulnerabilities', [])
                
            for v in vulns_list[:5]:
                pkg = v.get('packageName', 'Inconnu')
                version = v.get('version', '?')
                title = v.get('title', 'Faille dépendance')
                severity = v.get('severity', 'UNKNOWN').upper()
                details.append(f"📦 *[{severity}]* `{pkg}@{version}` -> {title}")
            return len(vulns_list), details
    except Exception:
        return "Erreur", ["❌ Impossible de lire le rapport Snyk"]

def parse_trivy():
    details = []
    try:
        with open('trivy-results.json', 'r') as f:
            data = json.load(f)
            total_vulns = 0
            for result in data.get('Results', []):
                vulns = result.get('Vulnerabilities', [])
                total_vulns += len(vulns)
                for v in vulns[:5]:
                    target = result.get('Target', 'Fichier')
                    vuln_id = v.get('VulnerabilityID', 'ID inconnu')
                    severity = v.get('Severity', 'UNKNOWN')
                    details.append(f"🐳 *[{severity}]* `{target}` -> {vuln_id}")
            return total_vulns, details
    except Exception:
        return "Erreur", ["❌ Impossible de lire le rapport Trivy"]

def send_telegram_message(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    semgrep_count, semgrep_details = parse_semgrep()
    snyk_count, snyk_details = parse_snyk()
    trivy_count, trivy_details = parse_trivy()

    # Construction du message principal
    msg = (
        "🛡️ *Rapport de Sécurité Détaillé DevSecOps*\n"
        "📌 *Projet :* `discovery-service-aerospace`\n"
        "───────────────────────\n\n"
    )

    # Section Semgrep
    msg += f"🔍 *Semgrep (SAST) :* `{semgrep_count}` trouvée(s)\n"
    if semgrep_details:
        msg += "\n".join(semgrep_details[:3]) + "\n"
    else:
        msg += "✔️ Aucun problème de code détecté.\n"
    msg += "\n───────────────────────\n\n"

    # Section Snyk
    msg += f"📦 *Snyk (SCA) :* `{snyk_count}` détectée(s)\n"
    if snyk_count != "Erreur" and snyk_details:
        msg += "\n".join(snyk_details[:3]) + "\n"
    elif snyk_count == "Erreur":
        msg += f"{snyk_details[0]}\n"
    else:
        msg += "✔️ Vos dépendances Maven sont sûres.\n"
    msg += "\n───────────────────────\n\n"

    # Section Trivy
    msg += f"🐳 *Trivy (Configuration) :* `{trivy_count}` détectée(s)\n"
    if trivy_details:
        msg += "\n".join(trivy_details[:3]) + "\n"
    else:
        msg += "✔️ Fichiers de configuration sains.\n"
    
    msg += "\n🚀 _Pipeline exécuté. Analyse complète disponible sur GitHub._"

    send_telegram_message(msg)
