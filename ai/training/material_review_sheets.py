"""Render legacy annotations for human review; never approve or change labels."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from audit_material_coverage import NAMES
from prepare_device_dataset import parse_label
from prepare_material_review import review_rows


def render(root, output, class_name=None):
    root, output = root.resolve(), output.resolve()
    if output == root or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Output must be separate from source dataset')
    rows = review_rows(root)
    if class_name:
        if class_name not in NAMES:
            raise ValueError('Unknown legacy class')
        rows = [r for r in rows if class_name in r['existing_classes'].split('|')]
    output.mkdir(parents=True, exist_ok=False)
    index = []
    for offset in range(0, len(rows), 12):
        sheet = Image.new('RGB', (1200, 1280), 'white')
        for slot, row in enumerate(rows[offset:offset + 12]):
            tile = Image.new('RGB', (400, 320), '#eeeeee')
            draw = ImageDraw.Draw(tile)
            error = None
            try:
                with Image.open(root / row['image']) as original:
                    if original.getexif().get(274, 1) != 1:
                        raise ValueError('EXIF orientation needs label review')
                    frame = original.convert('RGB')
                frame.thumbnail((396, 230))
                boxes = ImageDraw.Draw(frame)
                for line in (root / row['label']).read_text(encoding='utf-8-sig').splitlines():
                    if not line.strip():
                        continue
                    name, (cx, cy, w, h) = parse_label(line, NAMES)
                    x, y = (cx-w/2)*frame.width, (cy-h/2)*frame.height
                    boxes.rectangle((x, y, x+w*frame.width, y+h*frame.height), outline='red', width=2)
                    boxes.text((x, y), name, fill='yellow', stroke_width=1, stroke_fill='black')
                tile.paste(frame, (2, 0))
            except (OSError, ValueError) as exc:
                error = str(exc)
                draw.text((8, 40), 'REVIEW ERROR - see index.json', fill='red')
            number = offset + slot + 1
            draw.text((4, 234), f"#{number} {row['split']} PENDING", fill='black')
            draw.text((4, 250), Path(row['image']).name[:60], fill='black')
            draw.text((4, 266), row['existing_classes'][:60] or 'NEGATIVE: verify', fill='black')
            draw.text((4, 282), row['issue'][:60], fill='red')
            sheet.paste(tile, ((slot % 3)*400, (slot // 3)*320))
            index.append(row | {'number': number, 'sheet': f'sheet-{offset//12+1:03}.jpg', 'render_error': error})
        sheet.save(output / f'sheet-{offset//12+1:03}.jpg', quality=90)
    (output / 'index.json').write_text(json.dumps({'training_approved': False,
        'note': 'Legacy meanings only. Mixed_EWaste is NOT plastic body. Sheets are not source permission or approval.',
        'images': index}, indent=2), encoding='utf-8')
    return index


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--class-name', choices=NAMES)
    args = parser.parse_args()
    print(f'{len(render(args.data, args.output, args.class_name))} images rendered; no training or approval.')
