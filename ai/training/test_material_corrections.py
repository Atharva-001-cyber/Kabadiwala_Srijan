import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from apply_material_corrections import apply


class CorrectionTests(unittest.TestCase):
    def test_isolated_correction_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'source'
            root.mkdir()
            photo = root / 'motor.png'
            Image.new('RGB', (100, 100)).save(photo)
            original = photo.read_bytes()
            item = dict(image='motor.png', sha256=hashlib.sha256(original).hexdigest(),
                        width=100, height=100, class_id=5, box_xyxy=[10, 20, 90, 80])
            manifest = base / 'corrections.json'
            manifest.write_text(json.dumps({'corrections': [item]}))
            output = base / 'candidate'
            self.assertEqual(apply(root, manifest, output), 1)
            self.assertEqual(photo.read_bytes(), original)
            self.assertEqual((output / 'images/motor.png').read_bytes(), original)
            self.assertEqual((output / 'labels/motor.txt').read_text().split(),
                             ['5', '0.50000000', '0.50000000', '0.80000000', '0.60000000'])
            self.assertFalse(json.loads((output / 'review.json').read_text())['training_approved'])
            with self.assertRaises(ValueError):
                apply(root, manifest, output)
            for entries in ([item, item], [item | {'sha256': 'wrong'}],
                            [item | {'box_xyxy': [0, 0, 101, 80]}]):
                manifest.write_text(json.dumps({'corrections': entries}))
                rejected = base / 'rejected'
                with self.assertRaises(ValueError):
                    apply(root, manifest, rejected)
                self.assertFalse(rejected.exists())


if __name__ == '__main__':
    unittest.main()
