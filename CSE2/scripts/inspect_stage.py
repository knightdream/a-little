#!/usr/bin/env python3
"""Export Chinese stage data for inspection; never modifies runtime assets."""
import argparse
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('map', nargs='?', default='Start', help='Map basename, e.g. Start, Cave, Mimi')
args = parser.parse_args()
source = ROOT / 'game_chinese/data/Stage'
output = ROOT / '.local/map-inspection'
output.mkdir(parents=True, exist_ok=True)

def write_json(name, value):
    (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

stages = []
for line in (ROOT / 'src/StageChinese.inc').read_text().splitlines():
    if not line.startswith('{'):
        continue
    fields = [v.strip().strip('"') for v in line.strip('{},').split(',')]
    parts, name, background_type, background, npc, npc2, boss, title = fields
    title = bytes(int(v, 16) for v in re.findall(r'\\x([0-9A-Fa-f]{2})', title)).decode('gbk')
    b = (source / (name + '.pxm')).read_bytes()
    width, height = struct.unpack_from('<HH', b, 4)
    stages.append(dict(id=len(stages), map=name, name=title, tileset=parts,
        background=background, background_type=background_type,
        npc_sprites=[npc, npc2], boss_id=int(boss), width=width, height=height))
write_json('stages.json', stages)
stage = next((s for s in stages if s['map'] == args.map), None)
if stage is None:
    parser.error('Unknown map; see .local/map-inspection/stages.json')
name = stage['map']
b = (source / (name + '.pxm')).read_bytes()
assert b[:3] == b'PXM'
w, h = stage['width'], stage['height']
assert len(b) == 8 + w * h
rows = [list(b[8 + y * w:8 + (y + 1) * w]) for y in range(h)]
b = (source / (name + '.pxe')).read_bytes()
assert b[:3] == b'PXE'
count, = struct.unpack_from('<I', b, 4)
assert len(b) == 8 + count * 12
keys = ['x', 'y', 'flag_id', 'event_id', 'npc_type', 'bits']
entities = [dict(zip(keys, struct.unpack_from('<6H', b, 8 + i * 12))) for i in range(count)]
attributes = (source / (stage['tileset'] + '.pxa')).read_bytes()
write_json(name + '.json', dict(stage=stage, tile_size_pixels=16,
    coordinate_note='Zero-based tile coordinates; tiles[y][x] is a tile ID, not a collision type.',
    tiles=rows, entities=entities,
    tile_attributes={str(i): '0x%02X' % attributes[i] for i in sorted(set(sum(rows, [])))}))
b = (source / (name + '.tsc')).read_bytes()
half = len(b) // 2
key = b[half] or 7
plain = bytes(v if i == half else (v - key) & 255 for i, v in enumerate(b))
(output / (name + '.tsc.txt')).write_text(plain.decode('gbk'), encoding='utf-8')
print('Exported:', output / 'stages.json', output / (name + '.json'), output / (name + '.tsc.txt'), sep='\n')
