# Data dictionary

## Simulation paired-prediction archives

`E48_full_revision_v1`, `E50_corrected_dynamics_v1` and `E51_global_geometry_v1` store arrays in `paired_predictions.npz`. Keys encode `target_method_budget`. Each array has 128 rows and six columns:

1. columns 0:2: true difference between the two independent report repetitions;
2. columns 2:4: predicted report difference;
3. columns 4:6: predicted difference under the wrong-EEG control.

The report-difference score is `1 - sum((truth - prediction)**2) / sum(truth**2)`, summed across time/query and both report outputs. This is not ordinary absolute-output R² with a mean-subtracted denominator. Targets are averaged within each independent world/source cohort for inference.

The energy-matched `E58_energy_matched_v1` archive uses `predictions.npz` with key `target_method_mapping_calibration`. Shape is `(2, 2, 128, 2)`: the first axis selects truth versus prediction; the second selects independent repetition; then query and report output. The original implementation and result rows specify the exact order and both absolute and between-repeat metrics.

## EEG predictions

`raw_predictions/EEG_original.npz` and `EEG_corrected_history.npz` use keys `participant_method_budget`. Columns 0 and 1 are observed and predicted log response time. Remaining columns, when present, are auxiliary saved controls. Corrected history keys supersede original keys. Ordinary per-person R² uses the held-out person's mean only in the scoring denominator, not in prediction.

`E59_local_RT_v1/subject_XX/predictions.npz` stores observed and predicted log response time for nested-forward recording-2 checks and recording-2-to-3 prediction. Result JSON files retain fold selection, alpha choices, trial indices and scope.

## Derived EEG features

There are 26 `sub-*_run-*_features.npz` archives: 13 participants, recordings 2 and 3. Arrays include `x` (17-channel by eight early-bin EEG summaries, flattened), `u` (known inputs), `rt`, `kind`, `quality`, and `onset`. Associated JSON files describe the causal filter and extraction. The continuously filtered early window is 0–200 ms; filter state contains earlier raw observations. These are derived features, not raw continuous EEG, subjective reports or latent-state labels.

For response-time scoring, existing analyses require quality-passing correct target tones, onset at least eight seconds and response time 0.25–1.2 s. History-based methods build their predictor histories before selecting response-time-eligible scoring rows.

## Statistical records

Result JSON summaries contain actual per-cohort or per-participant values, recorded confidence intervals, raw/adjusted p-values and analysis scope. Export scripts verify means when individual values are supplied. Intervals are pointwise unless a named family explicitly supplies multiplicity-adjusted decisions. Default table reconstruction copies recorded intervals; it does not bootstrap them again.
