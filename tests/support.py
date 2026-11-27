"""Test content is independent of the author's live posts, pages, and lessons."""
from pathlib import Path
import shutil
from build import ROOT


def create_fixture(root):
    root=Path(root)
    shutil.copytree(ROOT/'templates',root/'templates')
    shutil.copy(ROOT/'site.json',root/'site.json')
    (root/'assets/files/semiconductors').mkdir(parents=True)
    for filename in ('style.css','course.css','course.js','portrait.svg'):
        shutil.copy(ROOT/'assets'/filename,root/'assets'/filename)
    pages=root/'content/pages';pages.mkdir(parents=True)
    (pages/'index.html').write_text('<h1>{{name}}</h1><p>{{institution}}</p><h2 id="information-title">More information</h2>{{contents}}{{latest_posts}}')
    (pages/'resume.md').write_text('## Education\n\nResume text.')
    course=root/'content/courses/semiconductors';course.mkdir(parents=True)
    (course/'course.yml').write_text('title: Semiconductor Notes\ndescription: ""\nchapters: []\n')
    (course/'overview.md').write_text('')
    (root/'content/posts').mkdir()
