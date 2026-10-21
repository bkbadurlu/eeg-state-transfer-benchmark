# EEG state transfer benchmark

Code and recorded outputs for a diagnostic evaluation of **geometry, cross-subject correspondence, and behavioral prediction** in controlled simulations and open EEG.

The framework asks three separate questions: does a representation preserve relationships between states, can corresponding states be matched across subjects, and does the resulting representation support prediction? Target-label calibration is evaluated separately. Stimulus identity is not treated as a subjective state label.

## Scope and principal observations

- Controlled systems include a folded surface, a circle, and a population model with a four-shell spherical EEG forward model. The latter is a simplified volume-conduction simulation, not an individual-MRI model.
- In the original 20 isometric-surface cohorts, mean between-repeat report-difference R² was 0.392 for Isomap and 0.168 for signal-rank PCA. Absolute-report R² was 0.222 and 0.382, respectively. These endpoints address different questions.
- A follow-up set used 20 new cohorts from the same generator family and matched calibration signal energy across anisotropy levels. The isometric repeat-difference result recurred; it does not establish robustness across independent generator families.
- The open-EEG application used OpenNeuro ds003061 v1.1.2, three fixed source participants and ten targets. Reliable improvement in response-time transfer was not established with the tested early features and label budgets. A separate tone-classification control does not validate response-time transfer.

These results support a diagnostic comparison of conditions and information budgets. They do not establish general superiority or inferiority of geometry-based methods, recovery of subjective feelings, or latent geometry discovery in measured EEG.

## Quickstart: reproduce recorded results without model training

Python 3.10.11 was used for the recorded analyses. The default reproduction needs only Python and NumPy. Commands below work in Windows PowerShell from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B reproduce.py
```

If NumPy is already installed, run `python -B reproduce.py` directly. Creating an environment and installing NumPy are optional preparation steps; the reproduction command itself does not install packages or access the network.

The command:

1. verifies the SHA256 manifest and Python source syntax;
2. reconstructs the original 15 groups of numeric CSV/LaTeX tables from audited summaries;
3. exports additional correspondence, sensory-control, sensitivity, and pooled-cohort summaries;
4. recomputes saved simulation and EEG prediction scores and compares them with the recorded results.

Outputs are written under `reproduced_tables/` and `outputs/`. LaTeX snippets are editable table fragments; **no LaTeX document is compiled**. Reconstructing tables retains recorded confidence intervals and adjusted p-values. It is not a new hypothesis test, a fresh bootstrap, or a model refit.

Individual steps are also available:

```powershell
python -B reproduce.py verify
python -B reproduce.py tables
python -B reproduce.py predictions
```

## Repository layout

| Path | Content |
| --- | --- |
| `reproduce.py` | Portable entry point for the checked reproduction steps |
| `reproduce_tables.py` | Original NumPy-only core-table reproduction code |
| `scripts/` | Integrity checks, additional table exports, prediction audits, and an isolated refit launcher |
| `inputs/` | Audited result summaries, including the later 40-cohort descriptive summary |
| `eeg_replication_tools/` | Original simulation/analysis code, local protocol records, completed result JSONs and prediction arrays |
| `raw_predictions/` | Original and corrected open-EEG prediction archives |
| `data_provenance/` | Dataset metadata, source-download records and a consolidated URL/size/SHA256 manifest |
| `docs/` | Information budgets, data dictionary, analysis map, correction history and refit instructions |
| `assets/` | Current graphical abstract and its mathematical/numeric provenance |
| `MANIFEST_SHA256.json` | Hashes of the distributed files, excluding generated output |

The package excludes raw EEG recordings, installed environments, model checkpoints, old manuscript drafts, reviewer/LLM conversations and private closed tests. The current manuscript source package is a separate deliverable.

## Information access

Ordinary simulation fits have measured observations and known inputs, with 48 source reports per source subject. Target report budgets are 0, 12 or 48. Ground-truth latent states and true pairs are available only to explicitly named diagnostic references and evaluation. The EEG target budgets are 0, 12 and 32. See [information budgets](docs/INFORMATION_BUDGETS.md) and the original protocol JSON files for the exact operations and label selection.

## Corrections and historical records

Use the audited summaries and corrected predictions selected by the reproduction scripts. In particular, the original simulation IPSID prototype is historical and is replaced by the corrected dynamics analysis. Two old EEG history arms used outcome-dependent history indexing and are replaced by the outcome-blind correction. The original three EEG primary contrasts are unaffected. Invalid rows are retained for traceability, not included as valid evidence. See [corrections](docs/CORRECTIONS.md).

Local plans and hashes document the recorded workflow; **they are not external preregistration**. Later diagnostic analyses were designed after earlier results were known. The original and follow-up simulation cohorts share a generator family; the EEG adequacy check reuses previously analyzed recordings.

## Model refitting

Default reproduction uses saved outputs. The code and plans needed for refitting are also supplied, but complete deep-model retraining is not part of the quickstart and has not been repeated in a clean installation for this release. See [refitting](docs/REFITTING.md) for environment records, isolated output folders and the distinction between reproducing scores and fitting models. Some original deep-model workers require CUDA and a separately isolated CEBRA 0.6.1 / NumPy 1 runtime.

## Data source and citation

Arnaud Delorme, *EEG data from an auditory oddball task*, OpenNeuro **ds003061 v1.1.2**, CC0: <https://doi.org/10.18112/openneuro.ds003061.v1.1.2>.

The repository contains derived early-EEG features, not the raw recordings. `data_provenance/OPENNEURO_RECORDINGS_SHA256.json` lists the 26 source recording URLs, byte sizes and observed SHA256 digests. Local download manifests are provenance records, not proof of ethical exemption. No new human recordings were collected.

See [CITATION.md](CITATION.md). This local release has no assigned repository URL, publication DOI or Zenodo DOI; none has been invented.

## Licensing and release status

The original research code has not yet been assigned a public reuse license by its author. No new MIT or other license is silently applied. See [LICENSE_STATUS.md](LICENSE_STATUS.md). OpenNeuro material retains its CC0 status. The included iVAE source retains its upstream MIT license and copyright notice; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This is a prepared repository package. It has not been uploaded or published by the packaging process. Repository creation, selection of a code license, author/citation details and an archival identifier remain release tasks for the author.
