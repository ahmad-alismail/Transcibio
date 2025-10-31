# Transcibio – Tool zur Audio-Transkription & Zusammenfassung

**Transcibio** ist eine leistungsstarke Anwendung zur Audiobearbeitung, die Spracherkennung, Sprechererkennung und Textzusammenfassung in einer benutzerfreundlichen Oberfläche vereint. Das Tool nutzt OpenAIs Whisper-Modelle für die Transkription, Pyannote zur Sprecheridentifikation und lokale Sprachmodelle (über LM Studio) für die Zusammenfassung.

Für eine detaillierte Anleitung, Features und Fehlerbehebung lesen Sie bitte die Datei [**Documentation.md**](Documentation.md).

---

## Schnellstart

### Voraussetzungen

- **Hugging Face API-Token:** Erforderlich für die Sprecher-Diarisierung.
- **LM Studio:** Erforderlich für die Erstellung von Zusammenfassungen.
- **Python 3.9+**
- **FFmpeg:** Muss installiert und im PATH Ihres Systems verfügbar sein.

### Installation

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/ahmad-alismail/Transcibio.git
    cd Transcibio
    ```

2.  **Virtuelle Umgebung einrichten:**
    ```bash
    python -m venv .venv
    # Unter Windows
    .venv\Scripts\activate
    # Unter Linux/macOS
    source .venv/bin/activate
    ```

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Anwendung starten:**
    ```bash
    streamlit run app.py
    ```

### Docker (Empfohlen)

Der einfachste Weg, die Anwendung zu starten, ist die Verwendung des vorgefertigten Docker-Images von Docker Hub.

1.  **Container direkt starten:**
    Führen Sie den folgenden Befehl aus. Docker lädt das Image automatisch herunter und startet es. Ersetzen Sie `DEIN_HF_TOKEN` durch Ihr Hugging Face Token.
    ```bash
    docker run --rm -p 8501:8501 -e HF_TOKEN="DEIN_HF_TOKEN" ahmad1289/transcibio:latest
    ```

2.  **Anwendung öffnen:**
    Greifen Sie auf die App unter `http://localhost:8501` zu.

#### Für Entwickler: Lokal bauen
Wenn Sie Änderungen am Code vornehmen möchten, können Sie das Image selbst bauen:
1.  **Docker-Image bauen:**
    ```bash
    docker build -t transcibio .
    ```

2.  **Container starten:**
    ```bash
    docker run --rm -p 8501:8501 -e HF_TOKEN="DEIN_HF_TOKEN" transcibio
    ```

---

Für eine detailliertere Einrichtung und Konfiguration lesen Sie bitte die [**vollständige Dokumentation**](Documentation.md).



