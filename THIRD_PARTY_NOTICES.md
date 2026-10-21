# Third-party notices

## iVAE

File: `eeg_replication_tools/revision_public_resources_20261019/ivae_official/models/nets.py`

Upstream: <https://github.com/ilkhem/iVAE>

Pinned commit: `cf6ff689f8ea957d70c54639132e3a875903a257`

SHA256: `fcb6ec5691538fe51de37c2a6c8f6156a8f5b3ff0b39f42a3ca90570bd1aa74d`

Copyright (c) 2019 Ilyes Khemakhem. MIT License. The complete upstream license is retained in `eeg_replication_tools/revision_public_resources_20261019/ivae_official/LICENSE`.

This source is included because the historical simulator import chain loads it, including in analyses that do not fit an iVAE model. It is not presented as original code.

## OpenNeuro ds003061

Author: Arnaud Delorme. Dataset: *EEG data from an auditory oddball task*. Version used: 1.1.2. License recorded by the source: CC0. DOI: <https://doi.org/10.18112/openneuro.ds003061.v1.1.2>.

Source metadata, event sidecars and derived EEG features are included with provenance. Raw EEG recording files are not included. Participant identifiers are the public dataset's identifiers; no new identifying information is added.

## External software

NumPy, SciPy, scikit-learn, PyTorch, MNE-Python, pyRiemann, PSID, POT, FUGW, CEBRA, pandas and Matplotlib are dependencies, not redistributed installations. Recorded versions and the isolated CEBRA runtime record are supplied under `docs/` and the requirements files. Credit their original publications and licenses as applicable.
