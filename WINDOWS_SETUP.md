# Run ZeroedIn Performance Lab on Windows

I designed ZeroedIn Performance Lab so Windows users can run the same application locally from the source repository. This setup keeps the Lab on your computer; it does not create a public account or upload your records to ZeroedIn.

## What you need

Install these two tools before beginning:

1. [Python 3.12](https://www.python.org/downloads/windows/) — choose the current Python 3.12.x Windows installer and select **Add python.exe to PATH** during installation.
2. [Node.js 22 LTS or newer](https://nodejs.org/en/download) — the standard Windows installer is appropriate.

You do not need PostgreSQL, Docker, an AI service, or a cloud account for the local showcase.

## Download the project

1. Open the [ZeroedIn Performance Lab repository](https://github.com/Rhayko/zeroedin-performance-lab).
2. Select **Code**, then **Download ZIP**.
3. Open your Downloads folder and choose **Extract All**. Do not run the project from inside the ZIP preview.
4. Open the extracted `zeroedin-performance-lab-main` folder. GitHub adds `-main` to the source ZIP folder name.
5. Right-click an empty area in that folder and choose **Open in Terminal**. On an older Windows version, click the folder address bar, enter `powershell`, and press Enter.

## Install the local dependencies

Copy and run each command in Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
npm --prefix frontend ci
```

The first installation downloads the project’s Python and JavaScript packages. It can take several minutes depending on the connection.

## Start the Lab

From the same project folder, run:

```powershell
.\.venv\Scripts\python.exe run_local.py
```

The launcher builds the interface, starts the local application at `http://127.0.0.1:8000`, and opens it in the default browser. Choose **Explore demo** to view fictional data or **Set up locally** to create an empty workspace.

Keep the terminal window open while using the Lab. Press `Ctrl+C` in that terminal to stop it. To return later, open a terminal in the same folder and run the start command again; the installation commands do not need to be repeated.

## Local data and privacy

The default Windows setup stores `zeroedin.db` in the extracted project folder. Use the interface’s JSON backup export before deleting, replacing, or moving a workspace you want to preserve.

The application binds only to `127.0.0.1`, so it is available from that Windows computer rather than the local network. If Windows Firewall displays a prompt, network sharing is not required for this local-only showcase.

Do not enter classified, operationally restricted, medical, or other sensitive information. This showcase is not a clinical system, military command system, personnel-management platform, or determination of duty fitness.

## Common Windows issues

- **`py` or Python 3.12 is not recognized:** install the current Python 3.12.x Windows release, select **Add python.exe to PATH**, and then open a new terminal.
- **`npm` is not recognized:** install the current Node.js LTS release, then open a new terminal.
- **Port 8000 is already in use:** close another running copy of the Lab, then run the start command again.
- **The browser did not open:** visit [http://127.0.0.1:8000](http://127.0.0.1:8000) manually while the terminal is still running.
- **You moved the project folder:** open the terminal from its new location before running the start command.

## What this guide provides

This runs the same V1 code and features as the macOS showcase: athlete or tactical profiles, daily check-ins, sleep and symptom context, exercise and training logs, repeatable performance tests, the 28-day baseline-building state, descriptive analytics, exploratory relationships, local backup, and restore.

It is a source-based Windows setup rather than a signed Windows installer. I will only label a packaged Windows release as validated after it has been built and tested on Windows.
