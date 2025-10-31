# Transcibio 

## Inhaltsverzeichnis

- [1. Einleitung und Projektziel](#1-einleitung-und-projektziel)
- [2. Bedienungsanleitung](#2-bedienungsanleitung)
- [3. Architektur und Anwendungsstruktur](#3-architektur-und-anwendungsstruktur)
- [4. Verwendete Technologien](#4-verwendete-technologien)
- [5. Installationsanleitung](#5-installationsanleitung)
- [6. Installation und Ausführung mit Docker (Empfohlen)](#6-installation-und-ausführung-mit-docker-empfohlen)

---

## 1. Einleitung und Projektziel

**Transcibio** ist eine Demonstrator-Anwendung, die im Rahmen des Forschungsprojekts **AI Traqc** an der **Hochschule Heilbronn** entwickelt wurde.

Die Anwendung konzentriert sich auf eine vollständig **lokale Verarbeitung** von Audiodaten, um Datenschutz und Unabhängigkeit von Cloud-Diensten zu gewährleisten.

### Kernfunktionen

*   **Automatische Transkription:** Umwandlung von gesprochener Sprache in Text mithilfe von OpenAIs Whisper-Modell.
*   **Sprecher-Diarisierung:** Erkennung und Zuordnung von Sprachsegmenten zu verschiedenen Sprechern ("Wer hat wann gesprochen?"). Dies wird durch `pyannote.audio` realisiert.
*   **KI-gestützte Zusammenfassung:** Erstellung von Inhaltszusammenfassungen der Transkripte durch ein lokal betriebenes Large Language Model (LLM) über LM Studio.

---

## 2. Bedienungsanleitung

Die Benutzeroberfläche ist in einen Hauptbereich für die Interaktion und eine Seitenleiste für die Konfiguration unterteilt.

### Schritt 1: Konfiguration in der Seitenleiste

Bevor Sie Audio verarbeiten, nehmen Sie die gewünschten Einstellungen in der linken Seitenleiste vor:

1.  **Transcription & Diarization:**
    *   **Whisper Model:** Wählen Sie ein Whisper-Modell. Größere Modelle (`large`) sind genauer, aber langsamer. Kleinere Modelle (`base`, `small`) sind schneller.
    *   **Number of Speakers:** Geben Sie die bekannte Anzahl der Sprecher an. Wenn die Anzahl unbekannt ist, belassen Sie den Wert bei `0` für eine automatische Erkennung.

2.  **Hugging Face (für Diarisierung):**
    *   Für die Sprecher-Diarisierung wird ein Hugging Face Token benötigt.
    *   Wenn das Token nicht automatisch gefunden wird, geben Sie es manuell in das passwortgeschützte Feld ein. Ohne Token ist die Diarisierung deaktiviert.

3.  **Summarization (LM Studio):**
    *   Stellen Sie sicher, dass **LM Studio** auf Ihrem Computer läuft, ein Modell geladen und der Server gestartet ist.
    *   **LM Studio API URL:** Geben Sie die URL Ihres LM-Studio-Servers ein (standardmäßig `http://localhost:1234/v1`).
    *   **Local Model Name:** Tragen Sie den Modell-Identifier ein, wie er in LM Studio angezeigt wird.

4.  **Summary Type:**
    *   Wählen Sie das gewünschte Format für die Zusammenfassung (z. B. Standard, Meeting-Protokoll).

### Schritt 2: Audioeingabe im Hauptbereich

Wählen Sie eine der beiden Methoden zur Audiobereitstellung:

*   **Upload File:** Laden Sie eine existierende `.wav`-Audiodatei hoch.
*   **Record Audio:** Nehmen Sie live Audio über Ihr Mikrofon auf.



### Schritt 3: Verarbeitung starten

1.  Klicken Sie auf den Button **"📊 Process Audio"**. Die Verarbeitung kann je nach Audiolänge und gewähltem Modell einige Zeit in Anspruch nehmen.
2.  Nach Abschluss wird das **sprecher-zugeordnete Transkript** im Hauptbereich angezeigt.

### Schritt 4: Zusammenfassung erstellen

1.  Wenn die Transkription erfolgreich war und LM Studio korrekt konfiguriert ist, erscheint der Button **"Generate Summary"**.
2.  **Konfigurieren Sie die Zusammenfassung:**
    *   **Summary Type:** Wählen Sie das gewünschte Format (z.B. Standard, Protokoll).
    *   **Customize Prompt (optional):** Klappen Sie den Bereich "⚙️ Customize Prompt (Advanced)" auf, um den für die Zusammenfassung verwendeten Text-Prompt anzupassen.
    *   **Detail Control (in der Seitenleiste):** Passen Sie die `Chunk Size` an, um die Detailtiefe zu steuern.
    *   **Generate Final Combined Summary (in der Seitenleiste):** Deaktivieren Sie diese Option, wenn Sie anstelle einer finalen Zusammenfassung die einzelnen Zusammenfassungen der Text-Chunks erhalten möchten.
3.  Klicken Sie auf **"Generate Summary"**, um die Zusammenfassung zu erstellen. Das Ergebnis wird darunter angezeigt. 



## 3. Architektur und Anwendungsstruktur

Die Anwendung ist als monolithischer Service konzipiert, der alle Aufgaben lokal ausführt. Die Architektur ist in drei logische Hauptkomponenten gegliedert:

1.  **Benutzeroberfläche (Frontend):**
    *   Erstellt mit **Streamlit**, einem Python-Framework zur schnellen Entwicklung von interaktiven Webanwendungen für Data Science und KI.
    *   Verantwortlich für die Konfiguration, Dateiuploads, Audioaufnahme und die Darstellung der Ergebnisse.

2.  **Verarbeitungspipeline (Backend-Logik):**
    *   Dies ist das Herzstück der Anwendung und orchestriert die verschiedenen KI-Modelle.
    *   Die Pipeline wird aktiviert, wenn der Benutzer auf "Process Audio" klickt.
    *   Sie folgt einem sequenziellen Ablauf:
        1.  **Audio-Input:** Empfängt die Audiodatei (Upload oder Aufnahme).
        2.  **Diarisierung:** `pyannote.audio` analysiert die Audiodatei und identifiziert die Zeitstempel der verschiedenen Sprecher.
        3.  **Transkription:** Das Whisper-Modell transkribiert den gesamten Audioinhalt zu Text.
        4.  **Alignierung:** Die Ergebnisse aus Diarisierung und Transkription werden zusammengeführt, um jedem Textsegment einen Sprecher zuzuordnen.

3.  **Zusammenfassung (LLM-Integration):**
    *   Diese Komponente ist von der Haupt-Pipeline entkoppelt.
    *   Sie kommuniziert über eine **HTTP-API** mit dem **LM Studio Server**.
    *   Der transkribierte Text wird in Blöcke (Chunks) aufgeteilt und an das LLM gesendet, um Teil-Zusammenfassungen zu erstellen, die am Ende zu einem Gesamttext kombiniert werden.

### Dateistruktur

Die Codebasis ist wie folgt organisiert:

Die Codebasis ist wie folgt organisiert:

*   `app.py`: Die Hauptdatei, die die Streamlit-Anwendung und die Benutzeroberfläche definiert.
*   `src/`: Ein Verzeichnis, das die Kernlogik enthält, aufgeteilt in Module:
    *   `processing.py`: Funktionen für Diarisierung, Transkription und Alignierung.
    *   `summarization.py`: Logik für die Kommunikation mit LM Studio und die Erstellung von Zusammenfassungen.
    *   `utils.py`: Hilfsfunktionen (z. B. Speichern von Dateien).
*   `config/prompts.yaml`: Enthält die anpassbaren Text-Prompts für die verschiedenen Zusammenfassungs-Typen.
*   `requirements.txt`: Listet alle Python-Abhängigkeiten des Projekts auf.

---

## 4. Verwendete Technologien

*   **Sprache:** Python 3.9+
*   **Web-Framework:** Streamlit
*   **Transkription:** [Whisper](https://github.com/openai/whisper) (Modelle von OpenAI, ausgeführt mit `faster-whisper`)
*   **Sprecher-Diarisierung:** [pyannote.audio](https://github.com/pyannote/pyannote-audio) (erfordert ein Hugging Face Token)
*   **Lokales Large Language Model (LLM):** [LM Studio](https://lmstudio.ai/) als Host für Modelle wie Llama, Mistral etc.
*   **Audioaufnahme:** `audiorecorder` (Streamlit-Komponente)

### Hardware-Anforderungen

Die Leistung der Anwendung hängt stark von Ihrer Hardware ab.

*   **RAM:** Mindestens 8 GB RAM sind für die kleineren Modelle (`tiny`, `small`) ratsam. Für größere Modelle (`medium`, `large`) werden 16 GB oder mehr empfohlen.
*   **GPU (Optional, aber empfohlen):** Die Transkription wird erheblich beschleunigt, wenn eine NVIDIA-GPU mit CUDA-Unterstützung verfügbar ist. Die `Dockerfile` und `requirements.txt` sind für die Nutzung von CUDA 11.8 konfiguriert. Ohne GPU läuft die Verarbeitung auf der CPU, was deutlich länger dauert.


## 5. Installationsanleitung

Um die Anwendung lokal auszuführen, sind mehrere Schritte erforderlich. Diese Anleitung setzt voraus, dass **Python 3.9** oder höher sowie **Git** auf Ihrem System installiert sind.

### Schritt 1: Systemabhängigkeiten installieren (FFmpeg)

FFmpeg ist eine Open-Source-Software zur Verarbeitung von Multimedia-Dateien. Es wird von den Audio-Bibliotheken in diesem Projekt benötigt, um Audiodateien zuverlässig zu lesen, zu konvertieren und zu verarbeiten.

*   **Windows:** Laden Sie es von der [offiziellen Website](https://ffmpeg.org/download.html) herunter und fügen Sie den `bin`-Ordner zu Ihrem System-PATH hinzu. Eine einfachere Methode ist die Installation über einen Paketmanager wie [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
*   **macOS:** Verwenden Sie [Homebrew](https://brew.sh/): `brew install ffmpeg`
*   **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`

### Schritt 2: Projekt-Repository klonen

Öffnen Sie ein Terminal und klonen Sie das Repository von GitHub:

```bash
git clone <URL_des_Repositorys>
cd <Name_des_geklonten_Ordners>
```

### Schritt 3: Python-Umgebung einrichten

Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden, um Abhängigkeitskonflikte zu vermeiden.

```bash
# Erstellen einer virtuellen Umgebung
python -m venv .venv

# Aktivieren der Umgebung
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### Schritt 4: Abhängigkeiten installieren

Installieren Sie alle benötigten Python-Pakete mit `pip`:

```bash
pip install -r requirements.txt
```


### Schritt 5: Hugging Face Token konfigurieren

Die Sprecher-Diarisierung mit `pyannote.audio` benötigt eine Authentifizierung bei Hugging Face.

1.  Erstellen Sie ein Konto auf [huggingface.co](https://huggingface.co/).
2.  Akzeptieren Sie die Nutzungsbedingungen für die Modelle [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization-py3.11) und [pyannote/segmentation](https://huggingface.co/pyannote/segmentation-py3.11).
3.  Erstellen Sie ein **Access Token** in Ihren Hugging Face-Profileinstellungen.
4.  **Optional (empfohlen):** Speichern Sie das Token als Umgebungsvariable `HF_TOKEN`, damit die Anwendung es automatisch laden kann. Alternativ können Sie es bei jeder Nutzung manuell in der Seitenleiste der Anwendung eingeben.

### Schritt 6: LM Studio einrichten (für Zusammenfassungen)

1.  Laden Sie **LM Studio** von [lmstudio.ai](https://lmstudio.ai/) herunter und installieren Sie es.
2.  Suchen und laden Sie in LM Studio ein passendes Modell herunter (z. B. `Mistral`, `Llama`).
3.  Wechseln Sie zum "Local Server"-Tab (Symbol `<->`).
4.  Wählen Sie das geladene Modell aus und starten Sie den Server durch Klick auf **"Start Server"**.
5.  Die angezeigte Server-URL (z.B. `http://localhost:1234/v1`) wird in der Transcibio-Anwendung benötigt.

### Schritt 7: Anwendung starten

Nachdem alle vorherigen Schritte abgeschlossen sind, starten Sie die Streamlit-Anwendung mit folgendem Befehl im Terminal:

```bash
streamlit run app.py
```

Die Anwendung sollte nun in Ihrem Webbrowser unter einer lokalen Adresse (z. B. `http://localhost:8501`) geöffnet werden.


## 6. Installation und Ausführung mit Docker (Empfohlen)

Die Verwendung von Docker ist die empfohlene Methode, da sie die Einrichtung vereinfacht und sicherstellt, dass alle Systemabhängigkeiten (wie z.B. `ffmpeg`) korrekt installiert sind.

### Voraussetzungen

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) muss installiert und gestartet sein.
*   Ein Hugging Face Token muss verfügbar sein.

### Methode 1: Vorgefertigtes Image von Docker Hub ausführen (Einfachste Methode)

Da das Image öffentlich auf Docker Hub verfügbar ist, müssen Sie es nicht selbst bauen. Sie können es mit einem einzigen Befehl herunterladen und starten.

1.  **Öffnen Sie ein Terminal.**

2.  **Starten Sie den Container:**
    Ersetzen Sie `DEIN_HF_TOKEN` durch Ihr persönliches Hugging Face Token.
    ```bash
    docker run --rm -p 8501:8501 -e HF_TOKEN="DEIN_HF_TOKEN" ahmad1289/transcibio:latest
    ```
    *   `docker run` lädt das Image `ahmad1289/transcibio:latest` automatisch herunter, falls es nicht lokal vorhanden ist.
    *   `-p 8501:8501`: Leitet den Port der Anwendung auf Ihren lokalen Rechner um.
    *   `-e HF_TOKEN="DEIN_HF_TOKEN"`: Übergibt Ihr Hugging Face Token an den Container.
    *   `--rm`: Löscht den Container automatisch, nachdem er beendet wurde.

3.  **Öffnen Sie die Anwendung** in Ihrem Browser unter `http://localhost:8501`.

### Methode 2: Image lokal bauen (Für Entwickler)

Wenn Sie den Code anpassen oder eine spezifische Version bauen möchten, folgen Sie diesen Schritten.

1.  **Klonen Sie das Projekt-Repository** (siehe Schritt 2 der lokalen Installation).

2.  **Öffnen Sie ein Terminal** im Hauptverzeichnis des Projekts.

3.  **Bauen Sie das Docker-Image.** Der Befehl unterscheidet sich je nach Systemarchitektur:
    *   **Für Standard-PCs (AMD64/x86_64):**
        ```bash
        docker build --build-arg TARGETPLATFORM=linux/amd64 -t transcibio .
        ```
    *   **Für Apple Silicon / ARM64:**
        ```bash
        docker build --build-arg TARGETPLATFORM=linux/arm64 -t transcibio .
        ```

4.  **Starten Sie den Container** aus dem lokal erstellten Image:
    ```bash
    docker run --rm -p 8501:8501 -e HF_TOKEN="DEIN_HF_TOKEN" transcibio
    ```

5.  **Öffnen Sie die Anwendung** in Ihrem Browser unter `http://localhost:8501`.

---
**Wichtiger Hinweis für beide Methoden:**

*   **Konfigurieren Sie LM Studio** wie in der lokalen Installationsanleitung beschrieben. Der Docker-Container kann standardmäßig auf den `localhost` Ihres Host-Systems zugreifen, sodass die Verbindung zu LM Studio funktioniert.