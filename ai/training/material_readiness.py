"""Read-only readiness report for the isolated material review, never train/deploy.

Run: python material_readiness.py --review ../../scratch/material-review-staging-v1
Exit 2 means review remains blocked, not a successful training run.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def inspect_review(root):
    root = Path(root)
    with (root / 'review.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    status = Counter(row.get('review_status', 'MISSING') for row in rows)
    buckets = Counter(row.get('bucket', 'MISSING') for row in rows)
    issues = Counter(issue for row in rows for issue in row.get('issue', '').split('|') if issue)
    missing = Counter()
    for row in rows:
        for field in ('source', 'use_permission', 'device_session_group', 'reviewer'):
            if not row.get(field, '').strip():
                missing[field] += 1
    return {
        'review_images': len(rows),
        'review_status_counts': dict(status),
        'bucket_counts': dict(buckets),
        'issue_counts': dict(issues),
        'missing_evidence_counts': dict(missing),
        'training_ready': False,
        'training_epochs': None,
        'notes': [
            'This legacy worklist alone cannot approve a new eight-material dataset.',
            'Pending means unreviewed, not training-approved.',
            'Mixed_EWaste is not E_Waste_Plastic_Body; reviewed replacement labels are required.',
            'Corrected labels, file hashes, class coverage and split independence need candidate validation.',
            'Training progress must come from the candidate run logs, not review counts.',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_review(args.review), indent=2))
    raise SystemExit(2)
