import fitz
import re
import csv
import json

doc = fitz.open('oxford_3000.pdf')
all_raw_lines = []

for pno, page in enumerate(doc):
    blocks = page.get_text('blocks')
    valid_blocks = [b for b in blocks if not (b[1] > 800 or (pno == 0 and b[1] < 100))]
    valid_blocks.sort(key=lambda b: (int(round(b[0] / 100)), b[1]))
    for b in valid_blocks:
        for l in b[4].split('\n'):
            l = l.strip().replace('\xa0', ' ').replace('\u2019', "'")
            if l:
                all_raw_lines.append((pno + 1, l))

# Identify wrapped lines
merged_lines = []
i = 0
while i < len(all_raw_lines):
    pno, line = all_raw_lines[i]
    if i + 1 < len(all_raw_lines):
        p_next, next_line = all_raw_lines[i + 1]
        # Check if current line ends with a continuation symbol or next line is a POS continuation
        if line.endswith(',') or line.endswith('/') or line.endswith('-') or next_line in ['adj.', 'number', 'v.', 'n.', 'adv.', 'pron.', 'article']:
            print(f"Merging: '{line}' + '{next_line}'")
            merged_lines.append((pno, line + ("" if line.endswith('/') else " ") + next_line))
            i += 2
            continue
    merged_lines.append((pno, line))
    i += 1

print(f"Total raw lines: {len(all_raw_lines)}")
print(f"Total merged lines: {len(merged_lines)}")

# Group into categories
categories = {'A1': [], 'A2': [], 'B1': [], 'B2': []}
current_cat = None

for pno, line in merged_lines:
    if line in ['A1', 'A2', 'B1', 'B2']:
        current_cat = line
    elif current_cat:
        categories[current_cat].append(line)

pos_pattern = re.compile(r'\s+(adj\.|adv\.|conj\.|det\.|det\./pron\.|det\./adj\.|det\./number|exclam\.|n\.|number|prep\.|prep\./adv\.|pron\.|v\.|modal\s+v\.|auxiliary\s+v\.|indefinite\s+article|definite\s+article)')

parsed = []
unsplit = []

for cat, items in categories.items():
    for item in items:
        m = pos_pattern.search(item)
        if m:
            word = item[:m.start()].strip()
            pos = item[m.start():].strip()
            parsed.append({'level': cat, 'word': word, 'pos': pos, 'raw': item})
        else:
            unsplit.append((cat, item))

print(f"Categories counts: { {k: len(v) for k, v in categories.items()} }")
print(f"Total words: {sum(len(v) for v in categories.values())}")
print(f"Successfully parsed: {len(parsed)}")
print(f"Unsplit: {len(unsplit)}")
if unsplit:
    for u in unsplit:
        print("  Unsplit:", u)
