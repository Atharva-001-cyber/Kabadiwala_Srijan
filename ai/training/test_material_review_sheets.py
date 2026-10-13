import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from material_review_sheets import render


class ReviewSheetTests(unittest.TestCase):
    def test_source_preserved_and_output_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'source'
            for split in ('train', 'val', 'test'):
                (root / split / 'images').mkdir(parents=True)
                (root / split / 'labels').mkdir()
            photo = root / 'train/images/cable.png'
            label = root / 'train/labels/cable.txt'
            Image.new('RGB', (100, 100)).save(photo)
            label.write_text('4 .5 .5 .5 .5')
            before = photo.read_bytes(), label.read_bytes()
            output = base / 'sheets'
            rows = render(root, output, 'Cable_Wire')
            self.assertEqual(len(rows), 1)
            self.assertIsNone(rows[0]['render_error'])
            self.assertFalse(json.loads((output / 'index.json').read_text())['training_approved'])
            self.assertEqual(before, (photo.read_bytes(), label.read_bytes()))
            self.assertTrue((output / 'sheet-001.jpg').is_file())
            with self.assertRaises(FileExistsError):
                render(root, output)
            with self.assertRaises(ValueError):
                render(root, root / 'sheets')


if __name__ == '__main__':
    unittest.main()
