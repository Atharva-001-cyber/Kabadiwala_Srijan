import csv
import tempfile
import unittest
from pathlib import Path
from material_readiness import inspect_review


class ReadinessTests(unittest.TestCase):
    def test_review_is_not_training_or_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'review.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=['review_status', 'bucket', 'issue'])
                writer.writeheader()
                writer.writerow({'review_status': 'PENDING', 'bucket': 'quarantine', 'issue': 'QUARANTINED_SOURCE'})
                writer.writerow({'review_status': 'APPROVED', 'bucket': 'pending_review', 'issue': ''})
            before = path.read_bytes()
            result = inspect_review(temp)
            self.assertEqual(result['review_images'], 2)
            self.assertEqual(result['missing_evidence_counts']['source'], 2)
            self.assertFalse(result['training_ready'])
            self.assertIsNone(result['training_epochs'])
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
