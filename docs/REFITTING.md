# Refitting and computational scope

## Recorded-output reproduction versus refitting

`python -B reproduce.py` checks files and recalculates scores from saved predictions. It does not train models. All supplied original scripts and local plans are retained without changing their scientific definitions or code hashes.

For a **new output copy** of an existing analysis, use the isolated launcher:

```powershell
python -B reproduce.py refit --analysis local-rt --output scratch_refits/local_rt_check
```

This requires `requirements-local-rt.txt`. The output path must not exist. The launcher copies the required immutable code/plans and 26 derived EEG feature archives there, checks available disk space, and runs the original `run` mode. It neither clears the recorded results nor creates a new plan. It reuses the original already-seen recordings and therefore is not independent validation.

Add `--dry-run` to either refit command to check its original plan/source hash and proposed output path without copying data or fitting models. Packaging validation checks both dry-run paths; it does not represent a completed model refit.

An analogous bounded same-plan energy-matched simulation refit is available:

```powershell
python -B reproduce.py refit --analysis energy --output scratch_refits/energy_check
```

The energy analysis uses 20 recorded seeds × four anisotropy ratios. It requires the full scientific environment because the original import chain loads PyTorch, MNE, pyRiemann and PSID even when it does not train a deep model. It may take substantial CPU time. No refit runs by default. Output folders need at least 3 GiB free space plus a 512 MiB working reserve and an estimated output allowance.

## Environment

- `requirements.txt`: NumPy-only table/prediction reproduction.
- `requirements-local-rt.txt`: bounded EEG adequacy refit.
- `requirements-full-recorded.txt`: versions observed in the original main runtime, not a claim that all hardware/platform combinations resolve identically.
- `docs/ENVIRONMENT_RECORDED.json`: Python/platform and package versions.
- `docs/CEBRA_ENVIRONMENT_RECORDED.json`: observed isolated CEBRA worker packages.

Original main runtime: Windows, Python 3.10.11, PyTorch 2.5.1+cu121. Existing CEBRA workers explicitly require CUDA, CEBRA 0.6.1 and their isolated NumPy 1 environment under `eeg_replication_tools/cebra061_runtime/site`. Installations and environments are not bundled. The complete original GPU benchmark has not been rerun in a clean environment as part of this packaging step. No silent CPU or alternative-method substitution is made.

## Original analysis map

| Script / directory prefix | Purpose |
| --- | --- |
| E48 | Main simulator and fixed-budget representation/alignment comparison; original IPSID prototype is superseded |
| E49 | Open-EEG response-time transfer |
| E49 correction | Outcome-blind predictor-history correction |
| E50 | Corrected input-driven dynamics comparison |
| E51 | Post hoc full-channel PCA and global correspondence diagnostics |
| E52–E53 | Mechanism/error metrics, matched source groups and null controls |
| E54–E55 | True-pair/frame, population-noise, sensory and output-calibration diagnostics |
| E56 | Fixed-reader map perturbations |
| E57 | Within-person encoder noise repeatability |
| E58 | New-seed calibration-energy-matched anisotropy analysis |
| E59 | Temporally ordered within-person EEG response-time adequacy check |

The isolated refit launcher is provided for E58/E59. The other original command-line scripts remain as archival research code; read their `main` functions before running them. Some historical scripts create their plan before execution or resume existing outputs. Running them directly in the distributed recorded-result directories is discouraged. The source closure contains earlier generator utilities because later analyses import them; it does not reopen older closed experiments.

Raw EEG is intentionally absent. For extraction, obtain only the versioned recordings and accompanying event files listed in `data_provenance/`, verify their digests, and use `real_eeg_extract_20261019.py` in an isolated working copy. The package does not download raw EEG automatically.

## Figure source provenance

`assets/` contains the current graphical abstract, actual cached coordinates/EEG bin means and numeric audit. `provenance/original_figure_code/` preserves the original drawing and evidence-replay scripts with their original working-tree path assumptions. These are provenance sources, not additional portable quickstart commands. Re-running the old manuscript builders is unnecessary for numeric reproduction and could overwrite a manuscript in a full development checkout.
