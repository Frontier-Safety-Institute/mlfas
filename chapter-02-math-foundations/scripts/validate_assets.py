"""Validate the FSI Chapter 2 SVG-primary, PNG-fallback asset convention."""
from pathlib import Path
import json, re, xml.etree.ElementTree as ET
from PIL import Image
import nbformat

root = Path(__file__).resolve().parents[1]
assets = root / 'images'
svgs = sorted(assets.glob('*.svg'))
pngs = sorted(assets.glob('*.png'))
assert len(svgs) == len(pngs) == 20, (len(svgs), len(pngs))
assert [p.stem for p in svgs] == [p.stem for p in pngs]
svg_ns = '{http://www.w3.org/2000/svg}'
for svg in svgs:
    dom = ET.parse(svg).getroot()
    assert dom.tag == svg_ns + 'svg', svg
    assert 'viewBox' in dom.attrib, svg
    assert not dom.findall(f'.//{svg_ns}image'), f'SVG contains raster image: {svg}'
    assert len(dom.findall(f'.//{svg_ns}path')) + len(dom.findall(f'.//{svg_ns}rect')) + len(dom.findall(f'.//{svg_ns}line')) > 0, f'SVG lacks vector geometry: {svg}'
    with Image.open(svg.with_suffix('.png')) as im:
        assert im.width >= 900 and im.height >= 250, f'PNG too small: {svg}'

refs=[]
books = sorted(root.glob('*.ipynb'))
assert len(books) == 7
for book in books:
    nb=nbformat.read(book,as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type != 'markdown':
            continue
        source = cell.source
        for src in re.findall(r'<source type="image/svg\+xml" srcset="(images/[^"]+\.svg)"',source):
            stem=Path(src).stem
            expected=f'images/{stem}.png'
            assert f'<img src="{expected}"' in source, (book,src)
            assert f'alt="' in source and '<picture>' in source and '</picture>' in source
            assert (root/src).exists() and (root/expected).exists(), src
            refs.append((book.name, src, expected))
        for link in re.findall(r'\]\(([^)]+)\)', source):
            if link.startswith(('https:', 'http:', '#')): continue
            target = (book.parent/link).resolve()
            assert target.exists(), (book.name,link)
assert len(refs) == 40, f'Expected 20 diagrams in combined + 20 in lessons, found {len(refs)}'
assert len({x[1] for x in refs}) == 20
assert all(x[1].endswith('.svg') and x[2].endswith('.png') for x in refs)
manifest=json.loads((root/'chapter.json').read_text())
assert manifest['images']=={'preferred':'svg','fallback':'png','count':20}
print(f'PASS: {len(svgs)} genuine vector SVG + {len(pngs)} PNG fallbacks; {len(refs)} dual-format picture references in {len(books)} valid notebooks.')
