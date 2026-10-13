# CRT replacement review, 2026-10-13

`prepare_crt_replacements.py` validates the exact 11-class source map and stages
CRT-only-labelled scenes from `dataset_devices_v44_reviewed` without changing
originals or class IDs. Original splits remain intact; no training YAML is emitted.

Run output: `scratch/crt-replacement-review-v1`, 74 images (58 train, 11 val,
5 test), 46 mixed-class scenes skipped. Annotated sheets are in
`scratch/crt-replacement-sheets-v1`. All samples remain pending review.

First sheet visually inspected: recognizable CRT monitors/TVs occur, unlike the
old quarantined source. Sample 8 also contains visible circuit boards not covered
by the CRT-only annotations. Therefore CRT-only LABELS do not establish that a
scene contains no other material targets. Review every scene and annotate all
relevant objects before training. Small/occluded/damaged examples need original
resolution checks. Preserve test split; do not tune on it. Permissions and
cross-dataset device/session duplication checks remain pending.

## Additional source research

- https://data.mendeley.com/datasets/77383kmdnw/1 : declares CC BY 4.0 and
  Plastic Waste among 12 classes. This does not establish separated electronic
  casing semantics; not imported as E_Waste_Plastic_Body.
- https://huggingface.co/datasets/akhil2808/YoloDataset : gated access requires
  agreement to contact-information sharing. No terms accepted or files fetched.
- https://zenodo.org/records/18022530 : battery-WEEE RGB/X-ray collection; source
  description does not establish the needed exposed magnet/casing coverage.
  No automatic mapping/import.

No new model epochs or frontend/model changes in this step.
