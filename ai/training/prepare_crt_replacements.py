"""Stage CRT-only device scenes for visual review, never training approval."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from prepare_device_dataset import NAMES, parse_label


def prepare(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists() or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Choose fresh output outside source')
    names = [line for line in (root/'data.yaml').read_text().splitlines() if line.startswith('names:')]
    if len(names) != 1 or ast.literal_eval(names[0].split(':', 1)[1].strip()) != NAMES:
        raise ValueError('Unexpected source class map')
    records = []
    skipped_mixed = 0
    for split in ('train', 'val', 'test'):
        for label in sorted((root/split/'labels').glob('*.txt')):
            parsed = [parse_label(line, NAMES) for line in label.read_text().splitlines() if line.strip()]
            classes = {name for name, _ in parsed}
            if 'CRT' not in classes:
                continue
            if classes != {'CRT'}:
                skipped_mixed += 1
                continue
            photos = [p for p in (root/split/'images').glob(label.stem+'.*') if p.suffix.lower() in ('.jpg','.jpeg','.png','.webp')]
            if len(photos) != 1:
                raise ValueError('Missing/ambiguous source image')
            photo = photos[0]
            if not photo.resolve().is_relative_to(root) or not label.resolve().is_relative_to(root):
                raise ValueError('Source outside dataset')
            with Image.open(photo) as im:
                im.load()
                if im.getexif().get(274, 1) != 1:
                    raise ValueError('Orientation needs review')
            records.append(dict(image=photo.relative_to(root).as_posix(), label=label.relative_to(root).as_posix(),
                sha256=hashlib.sha256(photo.read_bytes()).hexdigest(), split=split,
                review_status='PENDING', source_dataset=str(root), source_permission_review='PENDING',
                label_sha256=hashlib.sha256(label.read_bytes()).hexdigest()))
    output.mkdir(parents=True)
    for split in ('train','val','test'):
        for kind in ('images','labels'):
            (output/split/kind).mkdir(parents=True)
    for row in records:
        for field in ('image','label'):
            shutil.copy2(root/row[field], output/row[field])
    report = dict(training_approved=False, images=len(records), skipped_mixed_scenes=skipped_mixed,
        note='CRT ID 2 shared by both maps. Original split retained. Visual, permissions, session/duplicate review pending. No training YAML.', records=records)
    (output/'review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = prepare(args.data, args.output)
    print(json.dumps({k:v for k,v in report.items() if k != 'records'}, indent=2))
