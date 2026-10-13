# ZeroedIn Performance Lab

## Why I built this

I built ZeroedIn Performance Lab for athletes and tactical populations—including military personnel—who need to understand what their training, recovery, sleep, symptoms, occupational demands, and performance data is actually saying over time.

My primary goal is simple:

> I want to turn consistent observations into an honest, individualized picture of how an athlete or tactical professional is training, recovering, and performing—without hiding the process behind an arbitrary score.

Most performance dashboards rush to reduce a person to a single readiness number. I do not think that is responsible when the weighting is arbitrary, the individual has not established a personal baseline, or the model has not been validated. My approach is to begin with transparent measurement, build an individual reference range, and clearly explain what the available data can and cannot support.

Athletic and tactical performance overlap, but they are not interchangeable. Tactical personnel may face load carriage, protective equipment, field exercises, shift work, sleep restriction, heat, occupational tasks, and real operational consequences. I want the Lab to preserve that context instead of treating military personnel as athletes with a different label.

The Lab is designed to help me answer three practical questions:

1. **What has the person actually been doing?** I can review training volume, intensity, session load, occupational or field demands, sleep, symptoms, recovery observations, and testing history.
2. **How is the person changing relative to their own baseline?** I compare each individual to their previous observations rather than immediately judging them against a generic population.
3. **Which patterns deserve a closer look?** I can explore relationships such as sleep and self-reported wellness, while clearly stating that an association is not proof of cause and effect.

This is a longitudinal performance-intelligence workspace for sport and tactical settings. It is not a medical diagnostic tool, a determination of deployment or duty fitness, an automatic training prescription, or a disguised AI chatbot.

## How I use it

### 1. Build the individual profile

I begin with the person’s sport or tactical role, training or service history, physical context, and current objective. This gives later observations the context they need.

### 2. Complete a consistent daily check-in

I record sleep duration and quality, fatigue, stress, motivation, perceived recovery, soreness or discomfort, and useful context such as travel or illness. I try to collect these observations under similar conditions each day. Consistency is more useful than chasing a “perfect” answer.

### 3. Log the training that was performed

I capture the session type, duration, session RPE, exercises or tasks, sets or intervals, repetitions, external or carried load, set RPE, and repetitions in reserve. Tactical users can also document load carriage, field exercises, occupational tasks, terrain, heat, protective equipment, and other relevant duty context.

### 4. Repeat a small number of useful performance tests

I choose measures that can be repeated under a consistent protocol, such as a countermovement jump, broad jump, grip-strength test, sprint, time trial, estimated 1RM, loaded march, casualty drag, equipment carry, or occupational fitness assessment. I record the protocol and testing conditions because a number without context can be misleading.

### 5. Build an individual baseline

The first target is roughly 28 unique daily observations. During this period, the interface explicitly says `Baseline building: Day n/28`. I do not treat the early data as a mature individual profile. After the initial period, the baseline becomes a reference for understanding later changes, but it still needs to be interpreted in sport, duty, and operational context.

### 6. Review trends without overstating them

I use the dashboard to review rolling trends, training load, baseline deviations, and repeat-test history. Relationships are labeled exploratory. I reserve inferential claims for analyses with a defined question, assumptions, uncertainty, and an appropriate analysis plan. I reserve predictions for future models that have been honestly validated against unseen outcomes.

## What is included in V1

- Individual profile with sport or tactical discipline and performance/readiness objective
- Editable profile and correction controls for mistaken observations, sessions, and tests
- Daily state, sleep, and symptom observations
- Training sessions with set-level reps, load, RPE, and RIR
- Repeatable performance-test records and protocols
- An explicit 28-day baseline-building state
- Transparent session load, rolling trends, and baseline deviations
- Clearly labeled exploratory relationships
- A Scientific Claims Register documenting every displayed metric
- Prediction and outcome entities for future accuracy and calibration auditing
- A disabled prediction endpoint so unvalidated forecasts cannot appear in V1
- Responsive React interface and a PostgreSQL-ready FastAPI backend

I have deliberately left out LLM/chat features, automated prescriptions, arbitrary readiness scores, and active performance predictions.

## How I explain the analytics

- **Descriptive analytics** summarize what was recorded. Examples include session load, volume load, rolling averages, and changes from an individual baseline.
- **Exploratory analysis** helps me identify patterns worth investigating. It does not establish causation or guarantee that a pattern will continue.
- **Inferential analysis** would require a stated estimand, uncertainty intervals, sampling assumptions, missing-data decisions, and diagnostics. V1 does not present inferential conclusions.
- **Predictive analysis** would require a defined target and time horizon, temporal validation, benchmark comparisons, calibration and error reporting, model versioning, and preserved outcomes. Predictive output remains inactive.

The detailed rationale, assumptions, evidence requirements, limitations, and validation state for each metric live in [SCIENTIFIC_CLAIMS.md](SCIENTIFIC_CLAIMS.md).

## Project structure

- `frontend/` — the React, TypeScript, and Vite interface
- `backend/app/` — the FastAPI, Pydantic, SQLAlchemy, and analytics code
- `backend/tests/` — tests for important calculations and API behavior
- `SCIENTIFIC_CLAIMS.md` — my evidence and validation register
- `docker-compose.yml` — an optional local PostgreSQL service

The data model covers athlete, daily state, sleep, symptom, training session, exercise set, performance test, wearable metric, prediction, and outcome. SQLite keeps local development simple; setting `DATABASE_URL` switches the same persistence layer to PostgreSQL.

## Download the macOS showcase

If you want to explore the Lab without installing Python, Node.js, or developer tools, download my packaged macOS showcase:

[Download ZeroedIn Performance Lab for macOS](https://github.com/Rhayko/zeroedin-performance-lab/releases/latest/download/ZeroedIn-Performance-Lab-macOS.zip)

1. Download and unzip `ZeroedIn-Performance-Lab-macOS.zip`.
2. Drag **ZeroedIn Performance Lab** into Applications if you want to keep it there.
3. Because this portfolio build is not Apple-notarized, right-click the app the first time, choose **Open**, and confirm **Open**.
4. The app starts a private server on this computer and opens `http://127.0.0.1:8000` in the default browser.
5. Choose **Explore demo** for fictional data or **Set up locally** for an empty personal workspace.
6. Quit **ZeroedIn Performance Lab** from the Dock when you are finished.

The app stores its local database at `~/Library/Application Support/ZeroedIn Performance Lab/zeroedin.db`. Removing the app does not automatically remove that database. Export a JSON backup from the interface before deleting or moving records you want to preserve.

The current downloadable build targets Intel-based Macs. Apple silicon users may be prompted to install Rosetta. A native Apple silicon and Windows release can follow after this showcase build is validated across those systems.

## Running it locally

The following setup is for developers who want to inspect or modify the source code. I use Python 3.11+ and Node 20+.

After installing the dependencies once, I can build and launch the complete local application with one command:

```bash
.venv/bin/python run_local.py
```

This serves the application only on `127.0.0.1`, opens it in the default browser, and does not expose it to the local network.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`, and the interactive API documentation is available at `http://localhost:8000/docs`. When the database is empty, the interface creates a demo athlete with 19 days of coherent observations so the baseline and analytics can be reviewed immediately.

## Using PostgreSQL

```bash
docker compose up -d db
export DATABASE_URL=postgresql+psycopg://zeroedin:zeroedin@localhost:5432/zeroedin
cd backend
uvicorn app.main:app --reload
```

Before production schema changes, I will add a formal migration workflow such as Alembic. V1 currently uses automatic table creation to keep local setup straightforward.

## Verifying the build

```bash
cd backend
pytest

cd ../frontend
npm run build
```

## Current boundary

This software supports performance tracking and education for athletes and tactical populations, including military personnel. It does not diagnose injury or illness, replace qualified medical care, determine deployment or duty fitness, or guarantee a performance outcome. When I add stronger analytical claims in the future, I will document the evidence and validation required before those claims appear in the interface.
