# Scientific Claims Register

This register constrains what ZeroedIn Performance Lab V1 may say. Status values are **calculation validated**, **provisional**, or **inactive**. Product copy must not promote descriptive or exploratory output into an inferential or predictive claim.

| Metric or claim | Class | Rationale / definition | Evidence requirements | Assumptions | Limitations | Status |
|---|---|---|---|---|---|---|
| Session training load | Descriptive | Duration in minutes × session RPE, reported in arbitrary units | Correct implementation and transparent inputs | Session RPE is recorded consistently | Recall, anchoring, and construct interpretation affect RPE; not physiological “load” | Calculation validated |
| Set volume load | Descriptive | Sum of repetitions × external load in kg | Correct set-level records | Comparable exercise technique and ROM | Not mechanical work; ignores tempo, ROM, assistance, and internal response | Calculation validated |
| Individual baseline | Descriptive reference | First 28 unique daily observations define an initial within-person reference | Approximately 28 representative observations under stable measurement procedures | Collection period is representative | Baseline can be biased by illness, unusual training or operational periods, missingness, or behavioral changes | Provisional |
| Rolling trend | Descriptive | Seven-observation trailing arithmetic mean (three observations for repeated tests) | Correct time ordering | Observations are sufficiently comparable | Smooths peaks, lags rapid changes, and does not establish a meaningful change | Calculation validated |
| Baseline deviation | Descriptive | Current value minus mean of initial baseline window | Stable baseline and consistent scale | Baseline mean is an appropriate reference | No uncertainty interval; not a standardized or clinically meaningful difference | Provisional |
| Self-reported wellness composite | Descriptive | Mean of fatigue and stress (direction reversed), motivation, and recovery | Reliability review and construct validation before stronger use | Four items may be direction-aligned and summarized | Not a readiness score; equal weighting is a display convenience; components remain visible | Provisional |
| Sleep–wellness relationship | Exploratory | Contemporaneous Pearson sample correlation | Adequate paired observations, diagnostics, confounder plan, uncertainty | Linear relationship; independent/representative observations | Unadjusted and non-causal; small sample, outliers, autocorrelation, and multiple testing | Provisional |
| Performance prediction | Predictive | Future performance from prior longitudinal inputs | Preregistered target and horizon, temporal holdout, discrimination/error metrics, calibration, drift monitoring, documented intended use | To be established per model | No predictions may be displayed in V1 | Inactive |

## Validation gates

Inferential analysis requires a stated estimand, sampling model, missing-data strategy, uncertainty intervals, diagnostics, and multiplicity decisions. Predictive analysis additionally requires temporal external or holdout validation, baseline comparisons, error distribution reporting, calibration assessment, versioned features/model artifacts, and retained prediction–outcome pairs.

The `prediction` and `outcome` entities exist for future auditability. The V1 API rejects creation of user-facing predictions.
