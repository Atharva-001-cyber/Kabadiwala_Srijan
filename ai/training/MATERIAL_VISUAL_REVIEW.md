# Material visual review preparation

Generate read-only, annotated sheets with the legacy class meanings:

```powershell
python ai/training/material_review_sheets.py --data dataset_ewaste_v1 --output scratch/material-visual-review-next
```

The output must be a new directory outside the dataset. Each sheet has up to 12
images. `index.json` maps numbers to original paths, hashes, issues and rendering
errors. Source images and labels are never rewritten. Rendering is not approval;
all entries remain pending. Source permissions and device/session split review
are still required. Inspect originals when sheet resolution is insufficient.

## Local run, 2026-10-13

- 759 images, 64 sheets in `scratch/material-visual-review-v1`.
- No rendering errors. This does not establish semantic correctness.
- Sheet 001 inspected: several Battery examples visibly show stationary batteries;
  the first example includes NONSPILLABLE LEAD-ACID text. Generic Battery labels
  must not be interpreted as evidence of Li-ion chemistry.
- Other sheets have not yet been fully visually reviewed in this run.
- Mixed_EWaste remains a legacy class, not electronic plastic-body ground truth.
- No model training or app/model replacement performed by this tool.

Tests: `python -m unittest test_material_review_sheets test_material_review test_material_stage test_material_readiness`
from `ai/training`. The sheet test verifies original bytes are preserved and
existing output/source-directory targets are rejected.
