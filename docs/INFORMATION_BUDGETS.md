# Information budgets

| Analysis | Source labels | Target labels | Hidden state / true pairs |
| --- | --- | --- | --- |
| Ordinary controlled transfer | 48 reports per source; three sources | 0, 12 or 48 reports | Not available to ordinary fits |
| Within-person / true-pair diagnostic references | Explicitly specified in each reference | Reference-specific | Diagnostic access only; not comparable as an ordinary zero-label method |
| Open-EEG transfer | Eligible source response times; counts retained in result records | 0, 12 or 32 response times from recording 2 | No measured latent-state truth exists |
| EEG within-person adequacy control | One person's permitted earlier response times | Full eligible recording-2 labels for the recording-3 test | No latent-state labels |
| Sensory control | Standard/target-tone labels within person | Within-person classifier training | Tone identity is a stimulus label, not a feeling label |

Representations and maps can use observations and known inputs from the permitted calibration data. Source reports can supervise the source reader and explicitly supervised comparison methods. Target calibration reports are not hidden inside the zero-label budget. Protocols specify calibration-trial counts, history lengths, folds and nested subsets.

Simulation source and target groups are held fixed within a cohort. The two target scores are averaged before cohort-level inference. EEG confidence intervals condition on three fixed source participants and resample target participants; repeated source groups are not independent participant cohorts.

The geometric tests use state truth only for scoring and named references. High internal distance agreement is not point correspondence, and report calibration is not discovery of latent semantics.
