"""Responsibility: Prepare bounded, inert previews of explicitly authorized published artifacts.
No discovery, file copying, external fetching, HTML execution or page building.
"""
import csv
import io
from pathlib import Path
from urllib.parse import quote

MAX_BYTES=64*1024
MAX_ROWS=20
MAX_COLUMNS=12
MAX_CELL=300
IMAGES={'.png','.jpg','.jpeg','.svg'}


def prepare_artifact(root, relative, allowed, label=None):
    """Resolve one exact allowlisted relative path. The caller owns the publication root.

    URL is relative to that same root; the builder must resolve it for the report.
    Text/CSV are inert source data, not markup. No automatic discovery or preview of arbitrary files.
    """
    root=Path(root).resolve()
    if not isinstance(relative,str) or relative not in allowed or '\\' in relative or any(ord(c)<32 for c in relative):
        raise ValueError('Artifact not authorized')
    parts=relative.split('/')
    if any(p in {'','.','..'} for p in parts):
        raise ValueError('Invalid relative artifact path')
    path=root.joinpath(*parts)
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path,*path.parents] if p!=root and p.is_relative_to(root)) or not path.is_file():
        raise ValueError('Artifact must be a regular file within the publication root')
    suffix=path.suffix.lower()
    item={'name':path.name,'format':suffix[1:].upper() or '—','href':quote(relative,safe='/'),'label':label,'kind':'fallback','truncated':False}
    if suffix in IMAGES:
        item['kind']='image' # SVG is rendered only in an img element, never inline/object/iframe.
    elif suffix in {'.txt','.json','.csv'}:
        with path.open('rb') as f: raw=f.read(MAX_BYTES+1)
        truncated=len(raw)>MAX_BYTES
        try: text=raw[:MAX_BYTES].decode('utf-8-sig',errors='ignore' if truncated else 'strict')
        except UnicodeDecodeError: return item
        if '\x00' in text: return item
        if suffix=='.csv':
            try:
                records=csv.reader(io.StringIO(text),strict=True)
                header=next(records,[])
                if not header: return item
                width=min(len(header),MAX_COLUMNS)
                rows=[]
                for index,row in enumerate(records):
                    if index>=MAX_ROWS: truncated=True; break
                    if len(row)!=len(header): return item
                    truncated |= any(len(cell)>MAX_CELL for cell in row[:width])
                    rows.append([cell[:MAX_CELL] for cell in row[:width]])
                truncated |= len(header)>width or any(len(cell)>MAX_CELL for cell in header[:width])
                item.update(kind='csv',columns=[{'label':cell[:MAX_CELL]} for cell in header[:width]],rows=rows,truncated=truncated)
            except (csv.Error,UnicodeError): return item
        else: item.update(kind='text',text=text,truncated=truncated)
    # PDF and other formats deliberately use a download fallback; never embed active documents.
    return item
