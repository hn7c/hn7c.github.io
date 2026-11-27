"""Validate generated local links and basic document structure before publication."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import posixpath


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()
        self.duplicate_ids=set()
        self.h1_count=0
        self.missing_alt=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='h1': self.h1_count+=1
        if tag=='img' and 'alt' not in attrs: self.missing_alt+=1
        if 'id' in attrs:
            if attrs['id'] in self.ids:self.duplicate_ids.add(attrs['id'])
            self.ids.add(attrs['id'])
        for name in ('href','src'):
            if name in attrs:self.links.append(attrs[name])


def validate_site(directory):
    directory=Path(directory).resolve()
    documents={}
    for file in directory.rglob('*.html'):
        parser=Document();parser.feed(file.read_text(encoding='utf-8'))
        documents[file.relative_to(directory).as_posix()]=parser
    errors=[]
    for name,document in documents.items():
        if document.h1_count!=1:errors.append(f'{name}: expected one main heading, found {document.h1_count}')
        if document.duplicate_ids:errors.append(f'{name}: duplicate element IDs: {sorted(document.duplicate_ids)}')
        if document.missing_alt:errors.append(f'{name}: images need alt text (empty alt is valid for decoration)')
        for href in document.links:
            url=urlsplit(href)
            if url.scheme or url.netloc:continue
            path=unquote(url.path)
            if path.startswith('/'):
                errors.append(f'{name}: root-relative link breaks GitHub project paths: {href}');continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),path)) if path else name
            if target=='..' or target.startswith('../'):
                errors.append(f'{name}: link escapes the site: {href}');continue
            file=directory/target
            if file.is_dir():file=file/'index.html';target=file.relative_to(directory).as_posix()
            if not file.is_file():
                errors.append(f'{name}: missing local target: {href}');continue
            if url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
                errors.append(f'{name}: missing anchor: {href}')
    if errors:raise ValueError('Site validation failed:\n'+'\n'.join(errors))
    return len(documents)
