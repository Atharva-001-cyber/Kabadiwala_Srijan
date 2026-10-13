import json
from pathlib import Path
import tempfile
import unittest
from prepare_material_review import apply_visual_holds
from stage_material_review import BLOCKERS


class VisualHoldsTests(unittest.TestCase):
    def test_matching_hash_hold_and_changed_image_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'holds.json'
            manifest.write_text(json.dumps({'holds': [dict(image='train/images/a.jpg', sha256='abc', reason='Wrong box')]}))
            row = dict(image='train\\images\\a.jpg', sha256='abc', issue='REVIEW', review_status='PENDING')
            result = apply_visual_holds([row], manifest)[0]
            self.assertIn('VISUAL_LABEL_HOLD', result['issue'])
            self.assertIn('VISUAL_LABEL_HOLD', BLOCKERS)
            self.assertEqual(result['review_status'], 'PENDING')
            self.assertEqual(result['review_notes'], 'Wrong box')
            with self.assertRaises(ValueError):
                apply_visual_holds([row | {'sha256': 'changed'}], manifest)
            other = row | {'image': 'train/images/other.jpg'}
            self.assertEqual(apply_visual_holds([other.copy()], manifest), [other])


if __name__ == '__main__':
    unittest.main()
