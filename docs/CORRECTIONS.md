# Corrections, historical rows and valid outputs

## Simulation dynamics

The IPSID prototype in the original `E48_full_revision_v1` records used a coarse-grid mismatch. Corrected dynamics in `E50_corrected_dynamics_v1` supersede this prototype for the amended comparison. The audited `E48_E50_TAM_SONUC_OZETI.json` selects the valid amended rows. Prototype rows remain in the original archives for traceability; reproducing their arithmetic does not make them valid evidence. The amendment and protocol records are retained.

## EEG history selection

Two auxiliary history-based EEG arms in the original `E49_open_EEG_v1` selected histories using response-time eligibility. That gave indirect outcome-dependent access and invalidated those rows for the stated information budget. `E49_corrected_history_v1` constructs histories on the outcome-blind quality-passing oddball grid before choosing scoring trials.

`E49_HISTORY_CORRECTION_V2_20261019.json` documents the correction, first failed technical attempt and unchanged primary contrasts. The core reproduction overlays the corrected prediction arrays onto the original arrays by key before calculating all 480 valid method/budget/participant cells.

## Inferential status

The initial primary test families remain unchanged. Subsequent diagnostic analyses and the energy-matched new-seed replication were planned after earlier results were seen. Local timestamps and hashes are supplied as provenance, not external preregistration. The same-family 40-cohort pooled description does not replace the original 20-cohort tests or treat the two sets as paired.

Historical score records and protocol hashes are preserved byte-for-byte. Some JSON records therefore retain historical local file paths or partial execution snapshots; their directories and the final result records, rather than a historical snapshot's `RUNNING` string, determine completed scope.
