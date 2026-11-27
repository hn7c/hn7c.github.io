"""Create an unpublished Markdown post: python3 new_post.py optics 'My title'."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent


def create_post(section, title, published=None, root=ROOT):
    root = Path(root)
    sections = {item['slug'] for item in json.loads((root/'site.json').read_text())['sections']}
    if section not in sections:
        raise ValueError('Choose a section: '+', '.join(sorted(sections)))
    if not title.strip():
        raise ValueError('Title cannot be empty')
    published = date.fromisoformat(published) if published else date.today()
    plain = unicodedata.normalize('NFKD', title).encode('ascii','ignore').decode().lower()
    slug = re.sub(r'[^a-z0-9]+','-',plain).strip('-') or 'post'
    path = root/'content/posts'/section/f'{published}-{slug}.md'
    path.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation protects an existing post with the same name.
    with path.open('x',encoding='utf-8') as file:
        file.write(f'---\ntitle: {json.dumps(title,ensure_ascii=False)}\ndate: {published}\nsummary: "Add a short description."\ndraft: true\n---\n\nWrite your post here.\n')
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('title')
    parser.add_argument('--date',help='YYYY-MM-DD; defaults to today')
    args = parser.parse_args()
    try:
        path = create_post(args.section,args.title,args.date)
    except (ValueError,FileExistsError) as exc:
        parser.exit(1,f'Could not create post: {exc}\n')
    print(f'Created {path.relative_to(ROOT)}. Set draft: false when ready to publish.')
