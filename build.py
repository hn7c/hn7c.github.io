"""Build the static homepage and topic blogs from author-controlled content."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
import json
import re
import shutil
import tempfile

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import yaml
from teaching import build_course
from validate_site import validate_site

ROOT = Path(__file__).resolve().parent
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


class SiteLinks(Treeprocessor):
    """Resolve Markdown site links against the deploy root, including project sites."""
    def __init__(self, md, prefix):
        super().__init__(md)
        self.prefix = prefix

    def run(self, root):
        for element in root.iter():
            for attr in ('href', 'src'):
                value = element.get(attr)
                if value and not value.startswith(('#', '//')) and not urlsplit(value).scheme:
                    element.set(attr, self.prefix + value.lstrip('/'))


class SiteLinksExtension(Extension):
    def __init__(self, prefix):
        self.prefix = prefix
        super().__init__()

    def extendMarkdown(self, md):
        md.treeprocessors.register(SiteLinks(md, self.prefix), 'site_links', 5)


def render_markdown(text, prefix=''):
    return markdown.markdown(text, extensions=['extra', 'sane_lists', SiteLinksExtension(prefix)], output_format='html')


@dataclass
class Post:
    title: str
    date: date
    summary: str
    section: str
    slug: str
    body: str

    @property
    def url(self):
        return f'posts/{self.section}/{self.slug}.html'


def read_posts(root, sections):
    posts = []
    folder = root / 'content/posts'
    for source in sorted(folder.rglob('*.md')):
        if source.name.startswith('_'):
            continue
        section = source.parent.name
        if section not in sections or source.parent.parent != folder:
            raise ValueError(f'{source}: put posts directly in a configured section folder')
        if not SLUG.fullmatch(source.stem):
            raise ValueError(f'{source}: filename must use lowercase letters, digits, and single hyphens')
        parts = re.split(r'^---\s*$', source.read_text(encoding='utf-8'), maxsplit=2, flags=re.M)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError(f'{source}: expected YAML front matter between --- lines')
        meta = yaml.safe_load(parts[1])
        if not isinstance(meta, dict):
            raise ValueError(f'{source}: front matter must contain title, date, summary, and draft')
        draft = meta.get('draft', True)
        if not isinstance(draft, bool):
            raise ValueError(f'{source}: draft must be true or false, without quotes')
        if draft:
            continue
        title, summary = meta.get('title'), meta.get('summary', '')
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f'{source}: title is required')
        if not isinstance(summary, str):
            raise ValueError(f'{source}: summary must be text')
        try:
            published = date.fromisoformat(str(meta['date']))
        except (KeyError, ValueError) as exc:
            raise ValueError(f'{source}: date must be YYYY-MM-DD') from exc
        if not parts[2].strip():
            raise ValueError(f'{source}: published posts need a body')
        posts.append(Post(title.strip(), published, summary.strip(), section, source.stem, parts[2]))
    return sorted(posts, key=lambda post: (post.date, post.slug), reverse=True)


def date_label(value):
    return f'{value.day} {value:%B %Y}'


def post_list(posts, sections, prefix='', show_section=False):
    if not posts:
        return '<p class="empty-posts">No posts yet.</p>'
    items = []
    for post in posts:
        category = (f' · <a href="{prefix}{post.section}.html">{escape(sections[post.section]["title"])}</a>' if show_section else '')
        summary = f'<p>{escape(post.summary)}</p>' if post.summary else ''
        items.append(f'<li><h3><a href="{prefix}{post.url}">{escape(post.title)}</a></h3>'
                     f'<p class="post-meta"><time datetime="{post.date}">{date_label(post.date)}</time>{category}</p>{summary}</li>')
    return '<ul class="post-list">' + '\n'.join(items) + '</ul>'


def build(root=ROOT, output=None):
    root = Path(root).resolve()
    output = Path(output or root / 'dist').resolve()
    # Output is generated-only. Restrict it to a distinct child of the project.
    if output.parent != root or output.name in {'assets', 'content', 'templates', 'tests', '.github', '.openai', '.git'}:
        raise ValueError('Output must be a separate generated folder directly inside the project')
    config = json.loads((root / 'site.json').read_text())
    section_list = config['sections']
    sections = {section['slug']: section for section in section_list}
    if len(sections) != len(section_list) or any(not SLUG.fullmatch(slug) for slug in sections):
        raise ValueError('Section slugs must be unique lowercase URL names')
    children = {slug: [] for slug in sections}
    for section in section_list:
        parent = section.get('parent')
        if parent is not None:
            if parent not in sections or parent == section['slug'] or sections[parent].get('parent'):
                raise ValueError('Subsections must belong to an existing top-level section')
            children[parent].append(section)
    posts = read_posts(root, sections)
    updated = max([date.fromisoformat(config['updated'])] + [post.date for post in posts])
    template = Template((root / 'templates/page.html').read_text())
    # Build in a staging directory so a validation/render error leaves the old output intact.
    with tempfile.TemporaryDirectory(prefix='.site-build-', dir=root) as temporary:
        stage = Path(temporary)
        shutil.copytree(root / 'assets', stage / 'assets')
        (stage / '.nojekyll').touch()

        def page(path, title, body, active=None, description='', home=False, course=False):
            prefix = '../' * (len(Path(path).parts) - 1)
            navigation = [('index.html', 'Home'), ('resume.html', 'Resume'), ('archive.html', 'All posts'), ('index.html#information-title', 'All sections')]
            links = []
            for href, label in navigation:
                current = ' aria-current="page"' if href == active else ''
                links.append(f'<a href="{prefix}{href}"{current}>{label}</a>')
            header = '' if home or course else '<header><p>'+escape(config['name'])+'’s home page</p><nav aria-label="Main navigation">'+' &nbsp;|&nbsp; '.join(links)+'</nav><hr></header>'
            target = stage / path
            target.parent.mkdir(parents=True, exist_ok=True)
            extra_head = f'<link rel="stylesheet" href="{prefix}assets/course.css"><script defer src="{prefix}assets/course.js"></script>' if course else ''
            target.write_text(template.substitute(title=escape(title), name=escape(config['name']), institution=escape(config['institution']), description=escape(description), prefix=prefix, header=header, body=body, updated=date_label(updated), extra_head=extra_head, body_class='course-page' if course else ''), encoding='utf-8')

        home = (root / 'content/pages/index.html').read_text()
        home = home.replace('{{name}}',escape(config['name'])).replace('{{institution}}',escape(config['institution']))
        menu = '<ul class="contents"><li><a href="resume.html">Resume</a></li>'
        for section in section_list:
            if section.get('parent'):
                continue
            slug = section['slug']
            menu += f'<li><a href="{slug}.html">{escape(section["title"])}</a>'
            if children[slug]:
                menu += '<ul>' + ''.join(f'<li><a href="{child["slug"]}.html">{escape(child["title"])}</a></li>' for child in children[slug]) + '</ul>'
            menu += '</li>'
        menu += '</ul>'
        latest = '<section aria-labelledby="latest-title"><h2 id="latest-title">Latest posts</h2>'+post_list(posts[:5],sections,show_section=True)+'</section>' if posts else ''
        if '{{contents}}' not in home or '{{latest_posts}}' not in home:
            raise ValueError('Homepage must retain {{contents}} and {{latest_posts}} placeholders')
        page('index.html', 'Home', home.replace('{{contents}}',menu).replace('{{latest_posts}}',latest), home=True, description='Personal homepage, writing, and notes.')
        page('resume.html','Resume','<h1>Resume</h1>'+render_markdown((root/'content/pages/resume.md').read_text()),active='resume.html')
        course_shell = None
        for slug, section in sections.items():
            if slug == 'chips':
                course_shell = build_course(root, page, render_markdown, post_list([p for p in posts if p.section == slug], sections), section['title'])
                continue
            intro = root / f'content/pages/{slug}.md'
            legacy = '<div class="section-intro">'+render_markdown(intro.read_text())+'</div>' if intro.exists() else ''
            included = {slug} | {child['slug'] for child in children[slug]}
            section_posts = [post for post in posts if post.section in included]
            parent_link = ''
            if section.get('parent'):
                parent = sections[section['parent']]
                parent_link = f'<p><a href="{parent["slug"]}.html">{escape(parent["title"])}</a> / {escape(section["title"])}</p>'
            subnav = ''
            if children[slug]:
                subnav = '<nav aria-label="Subsections">' + ' &nbsp;|&nbsp; '.join(f'<a href="{child["slug"]}.html">{escape(child["title"])}</a>' for child in children[slug]) + '</nav>'
            description = f'<p>{escape(section["description"])}</p>' if section['description'] else ''
            body = f'{parent_link}<h1>{escape(section["title"])}</h1>{description}{legacy}{subnav}<section aria-labelledby="posts-title"><h2 id="posts-title">Posts</h2>'+post_list(section_posts,sections,show_section=bool(children[slug]))+'</section>'
            page(f'{slug}.html',section['title'],body,description=section['description'])
        page('archive.html','All posts','<h1>All posts</h1><p>Writing and notes, newest first.</p>'+post_list(posts,sections,show_section=True),active='archive.html')
        for post in posts:
            section = sections[post.section]
            prefix = '../../'
            body = f'<article class="blog-post"><h1>{escape(post.title)}</h1><p class="post-meta"><time datetime="{post.date}">{date_label(post.date)}</time> · <a href="{prefix}{post.section}.html">{escape(section["title"])}</a></p><div class="post-body">'+render_markdown(post.body,prefix)+f'</div></article><hr><p><a href="{prefix}{post.section}.html">All posts in {escape(section["title"])}</a></p>'
            if post.section == 'chips' and course_shell:
                body = course_shell(body,prefix,breadcrumb=' / '+escape(post.title))
                page(post.url,post.title,body,description=post.summary,course=True)
            else:
                page(post.url,post.title,body,description=post.summary)
        # Keep the user's extensionless Political Analysis URL functional too.
        page('intpoli/index.html','Political Analysis','<h1>Political Analysis</h1><p><a href="../intpoli.html">Read Political Analysis posts</a></p>')
        validate_site(stage)
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage,output)
    return len(posts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Generated output directory, directly inside the project')
    args = parser.parse_args()
    try:
        count = build(output=args.output)
    except (ValueError, yaml.YAMLError) as exc:
        parser.exit(1,f'Build failed: {exc}\n')
    print(f'Built homepage, resume, topic pages, archive, and {count} published post(s).')
