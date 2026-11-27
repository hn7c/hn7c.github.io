"""Ordered teaching notes, generated from a manifest and editable Markdown."""
from html import escape
from pathlib import Path
import re
import yaml

SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
FOLDER = Path('content/courses/semiconductors')


def read_course(root):
    folder = root / FOLDER
    course = yaml.safe_load((folder / 'course.yml').read_text())
    if not isinstance(course, dict) or not isinstance(course.get('chapters'), list):
        raise ValueError('Course needs a chapters list')
    for field in ('title', 'description'):
        if not isinstance(course.get(field), str):
            raise ValueError(f'Course needs a {field}')
    lessons, seen = [], set()
    for chapter_number, chapter in enumerate(course['chapters'], 1):
        if not isinstance(chapter, dict) or not isinstance(chapter.get('title'), str) or not isinstance(chapter.get('lessons'), list):
            raise ValueError('Each chapter needs a title and lessons list')
        for section_number, slug in enumerate(chapter['lessons'], 1):
            if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in seen:
                raise ValueError('Lesson slugs must be unique lowercase URL names')
            seen.add(slug)
            source = folder / f'{slug}.md'
            if not source.is_file():
                raise ValueError(f'Missing lesson: {slug}')
            parts = re.split(r'^---\s*$', source.read_text(), maxsplit=2, flags=re.M)
            if len(parts) != 3 or parts[0].strip():
                raise ValueError(f'{slug}: expected YAML front matter')
            meta = yaml.safe_load(parts[1])
            if not isinstance(meta, dict) or not isinstance(meta.get('title'), str) or not meta['title'].strip():
                raise ValueError(f'{slug}: title is required')
            body = parts[2].split('<!-- practice -->')
            if len(body) > 2 or not body[0].strip():
                raise ValueError(f'{slug}: provide notes, with at most one optional <!-- practice --> separator')
            if len(body) == 1:
                body.append('')
            downloads = meta.get('downloads', [])
            if not isinstance(downloads, list):
                raise ValueError(f'{slug}: downloads must be a list')
            for item in downloads:
                if not isinstance(item, dict) or not isinstance(item.get('label'), str) or not isinstance(item.get('file'), str):
                    raise ValueError(f'{slug}: each download needs label and file')
                asset = (root / item['file']).resolve()
                if not asset.is_relative_to((root / 'assets').resolve()) or not asset.is_file():
                    raise ValueError(f'{slug}: download must exist inside assets: {item["file"]}')
                item['file'] = asset.relative_to(root).as_posix()
            summary = meta.get('summary', '')
            if not isinstance(summary, str):
                raise ValueError(f'{slug}: summary must be text')
            lessons.append(dict(number=f'{chapter_number}.{section_number}', summary=summary, slug=slug, title=meta['title'], chapter=chapter['title'], notes=body[0], practice=body[1], downloads=downloads))
    return course, lessons


def build_course(root, page, markdown, posts, section_title):
    course, lessons = read_course(root)
    by_slug = {lesson['slug']: lesson for lesson in lessons}
    title = escape(course['title'])
    practice_lessons = [lesson for lesson in lessons if lesson['practice'].strip()]
    all_downloads = {item['file']: item['label'] for lesson in lessons for item in lesson['downloads']}

    def lesson_url(lesson, mode='notes'):
        suffix = '-practice' if mode == 'practice' else ''
        return f'notes/semiconductors/{lesson["slug"]}{suffix}.html'

    def shell(body, prefix='', breadcrumb='', controls='', mode='notes'):
        top = f'<nav class="course-topbar" aria-label="Course navigation"><a class="course-brand" href="{prefix}chips.html">{title}</a>'
        for chapter in course['chapters']:
            chapter_lessons = [by_slug[slug] for slug in chapter['lessons'] if mode != 'practice' or by_slug[slug]['practice'].strip()]
            if not chapter_lessons:
                continue
            top += f'<details class="chapter-menu"><summary>{escape(chapter["title"])}</summary><ul>'
            for item in chapter_lessons:
                top += f'<li><a href="{prefix}{lesson_url(item,mode)}">{item["number"]} {escape(item["title"])}</a></li>'
            top += '</ul></details>'
        download_link = f'<a href="{prefix}chips.html#downloads">Downloads</a>' if all_downloads else ''
        top += f'<a href="{prefix}index.html#information-title">All sections</a><span class="course-tools">{download_link}<button type="button" data-print hidden>Print</button></span></nav>'
        return f'{top}<div class="breadcrumbs"><a href="{prefix}index.html">Home</a> / <a href="{prefix}chips.html">{escape(section_title)}</a>{breadcrumb}</div>{controls}<div class="course-paper">{body}</div>'

    def index_controls(mode):
        return '<nav class="content-navigation" aria-label="Course material">' + ''.join(f'<a href="{path}"'+(' aria-current="page"' if mode == key else '')+f'>{label}</a>' for key,path,label in [('notes','chips.html','Notes'),('practice','chips-practice.html','Practice Problems')] if key == 'notes' or practice_lessons) + ('<a href="chips.html#downloads">Downloads</a>' if all_downloads else '') + '</nav>'

    intro = markdown((root / FOLDER / 'overview.md').read_text())
    for mode in ('notes','practice'):
        body = f'<h1>{title}' + (' : Practice Problems' if mode == 'practice' else '') + '</h1>'
        if mode == 'notes':
            body += (f'<p>{escape(course["description"])}</p>' if course['description'] else '') + intro
        elif practice_lessons:
            body += '<p>Select a section below to work through its practice problems. Each problem has a solution you can reveal after trying it yourself.</p>'
        if not practice_lessons and mode == 'practice':
            body += '<p class="empty-posts">No practice problems yet.</p>'
        for number, chapter in enumerate(course['chapters'],1):
            chapter_lessons = [by_slug[slug] for slug in chapter['lessons'] if mode != 'practice' or by_slug[slug]['practice'].strip()]
            if not chapter_lessons:
                continue
            body += f'<section class="chapter"><h2>Chapter {number} : {escape(chapter["title"])}</h2>'
            for lesson in chapter_lessons:
                summary = ' – '+escape(lesson['summary']) if lesson['summary'] else ''
                body += f'<p class="topic-description"><a href="{lesson_url(lesson,mode)}">{escape(lesson["title"])}</a>{summary}</p>'
            body += '</section>'
        if mode == 'notes':
            if all_downloads:
                body += '<section id="downloads"><h2>Downloads</h2><ul>' + ''.join(f'<li><a href="{escape(file)}">{escape(label)}</a></li>' for file,label in all_downloads.items()) + '</ul></section>'
            body += '<section class="course-posts"><h2>Posts</h2>'+posts+'</section>'
        path = 'chips.html' if mode == 'notes' else 'chips-practice.html'
        page(path,course['title'],shell(body,controls=index_controls(mode),mode=mode),description=course['description'],course=True)

    for lesson in lessons:
        prefix = '../../'
        for mode in ('notes', 'practice'):
            if mode == 'practice' and not lesson['practice'].strip():
                continue
            sequence = practice_lessons if mode == 'practice' else lessons
            index = sequence.index(lesson)
            controls = '<nav class="content-navigation" aria-label="Lesson material">'
            if index > 0:
                previous = sequence[index-1]
                controls += f'<a rel="prev" href="{prefix}{lesson_url(previous,mode)}" title="{escape(previous["title"])}">Prev. Section</a>'
            else:
                controls += '<span class="disabled">Prev. Section</span>'
            for key, label in (('notes', 'Notes'), ('practice', 'Practice Problems')):
                if key == 'practice' and not lesson['practice'].strip():
                    continue
                active = ' aria-current="page"' if key == mode else ''
                controls += f'<a{active} href="{prefix}{lesson_url(lesson,key)}">{label}</a>'
            controls += f'<a href="{prefix}chips.html">Contents</a>'
            if index+1 < len(sequence):
                following = sequence[index+1]
                controls += f'<a rel="next" href="{prefix}{lesson_url(following,mode)}" title="{escape(following["title"])}">Next Section</a>'
            else:
                controls += '<span class="disabled">Next Section</span>'
            controls += '</nav>'
            downloads = ''
            if lesson['downloads']:
                downloads = '<p class="lesson-downloads">' + ' · '.join(f'<a href="{prefix}{item["file"]}">{escape(item["label"])}</a>' for item in lesson['downloads']) + '</p>'
            heading = f'Section {lesson["number"]} : {escape(lesson["title"])}' + (' — Practice Problems' if mode == 'practice' else '')
            solution_controls = '<div class="solution-controls" hidden><button type="button" data-solutions="show">Show All Solutions</button><span> | </span><button type="button" data-solutions="hide">Hide All Solutions</button></div>'
            body = f'{solution_controls}<h1>{heading}</h1>{downloads}<article class="lesson-body">{markdown(lesson[mode],prefix)}</article>'
            breadcrumb = f' / {escape(lesson["chapter"])} / <strong>{escape(lesson["title"])}</strong>'
            page(lesson_url(lesson,mode), lesson['title'] + (' — Practice' if mode == 'practice' else ''), shell(body,prefix,breadcrumb,controls,mode),course=True)

    return shell
