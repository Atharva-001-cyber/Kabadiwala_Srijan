import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from prepare_crt_replacements import prepare
from prepare_device_dataset import NAMES


class CrtTests(unittest.TestCase):
    def test_splits_mixed_exclusion_and_map_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base/'source'
            for split in ('train','val','test'):
                (root/split/'images').mkdir(parents=True)
                (root/split/'labels').mkdir()
                Image.new('RGB',(20,20)).save(root/split/'images/crt.png')
                (root/split/'labels/crt.txt').write_text('2 .5 .5 .8 .8\n' + ('4 .5 .5 .2 .2' if split == 'val' else ''))
            (root/'data.yaml').write_text('names: '+json.dumps(NAMES))
            output = base/'review'
            report = prepare(root, output)
            self.assertEqual(report['images'],2)
            self.assertEqual(report['skipped_mixed_scenes'],1)
            self.assertEqual({r['split'] for r in report['records']},{'train','test'})
            self.assertFalse(report['training_approved'])
            self.assertEqual((root/'test/labels/crt.txt').read_bytes(),(output/'test/labels/crt.txt').read_bytes())
            with self.assertRaises(ValueError):
                prepare(root, output)
            (root/'data.yaml').write_text('names: ["Wrong"]')
            with self.assertRaises(ValueError):
                prepare(root, base/'bad')


if __name__ == '__main__':
    unittest.main()
