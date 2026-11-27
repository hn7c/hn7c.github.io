# Personal homepage and topic blogs

A GitHub Pages website with a plain early-2000s academic style: white background, Times text, blue links, and simple document layouts. All personal details remain placeholders. The homepage links to Resume and the topic blogs. Bristol, Aston Martin — DB Series, and Hongqi are nested under Vintage Cars.

**To publish a post, add one Markdown file. You do not edit the menu, archive, or generated HTML.**

## Easiest way: edit on GitHub

Once this project is in your GitHub repository:

1. Open the relevant folder under `content/posts/`, for example `content/posts/optics/`.
2. Choose **Add file → Create new file**. Name it `2026-11-25-my-first-note.md` (lowercase letters, numbers, and hyphens).
3. Copy the example below, change the title/date/summary, and write your post.
4. Use `draft: false` when ready. Commit the file to `main`.
5. The included GitHub Actions workflow rebuilds the site and publishes it. New posts appear on their topic page, the all-posts archive, and the homepage’s latest-posts list.

```markdown
---
title: "A note on optical interference"
date: 2026-11-25
summary: "A short introduction to what this note covers."
draft: false
---

Write your introduction here.

## Main idea

Use **bold**, *italics*, lists, quotations, tables, and links.

- First observation.
- Second observation.

## References

- [Source title](https://example.com)
```

Each folder has an `_template.md` to copy. Files whose names begin with `_` are never published: **create a new file with a different name**, rather than editing the template in place. Posts with `draft: true` (or no `draft` field) are also excluded. Draft files are still visible to anyone who can read your GitHub repository; this setting only hides them from the generated website.

Edit an existing Markdown file to update a post. Keep its filename and folder unchanged to preserve its URL. Delete the Markdown file to remove the post from the site and all lists. Dates control ordering; a future date does not schedule publication.

## Topic folders

| Page | Post folder |
| --- | --- |
| Work | `content/posts/work/` |
| Cat pictures | `content/posts/cats/` |
| Forensic Sciences | `content/posts/forensics/` |
| Semiconductors | `content/posts/chips/` |
| Optics | `content/posts/optics/` |
| Emergency Vehicle Lighting | `content/posts/emergency-lighting/` |
| Mathematics | `content/posts/mathematics/` |
| Economics | `content/posts/econ/` |
| Art History | `content/posts/art/` |
| Resources for Academia | `content/posts/recs/` |
| Sartorial | `content/posts/sartorial/` |
| Rowing | `content/posts/rowing/` |
| Cycling | `content/posts/cycling/` |
| Political Analysis | `content/posts/intpoli/` |
| Fine Firearms | `content/posts/firearms/` |
| Vintage Boats | `content/posts/boats/` |
| Vintage Cars (general posts) | `content/posts/cars/` |
| Vintage Cars — Bristol | `content/posts/bristol/` |
| Vintage Cars — Aston Martin — DB Series | `content/posts/db-am/` |
| Vintage Cars — Hongqi | `content/posts/hongqi/` |

The Vintage Cars page combines its general posts with Bristol, Aston Martin — DB Series, and Hongqi posts, newest first. Each subsection also has its own filtered blog page. Every post appears only once in the global archive. The public title is “Aston Martin — DB Series”; the existing `db-am.html` URL and `content/posts/db-am/` folder remain stable.

Resume remains a static page. Political Analysis uses `intpoli.html` in the menu; the original extensionless `intpoli/` path also works.

## Photos and links

Upload images into `assets/images/`. Reference them in Markdown using paths relative to the site root:

```markdown
![My cat asleep beside a book](assets/images/cat-asleep.jpg)

[My resume](resume.html)

[A related post](posts/optics/2026-11-25-my-first-note.html)
```

The builder adjusts Markdown links and images for nested post pages and GitHub project URLs. External URLs and `#fragment` links are retained. Raw HTML is supported for trusted author-written content, but its links are not rewritten; use Markdown links and images for automatic path handling. Start body headings with `##`; the post title already supplies the page’s `h1`.

## Local writing and preview

Requires Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python new_post.py optics "A note on optical interference"
# Edit the newly created file; set draft: false when ready.
python build.py
python -m http.server 8000 --directory dist
```

Visit `http://localhost:8000`. Rebuild after editing. The helper creates drafts and refuses to overwrite existing files. For a specific date, append `--date 2026-11-25`.

## Personalize the site

- `content/pages/index.html`: homepage intro, photo, contacts. Keep `{{contents}}` and `{{latest_posts}}` in place; the builder fills these in.
- `content/pages/resume.md`: resume content in Markdown.
- `content/pages/work.md`, `content/pages/cats.md`: optional introductions in Markdown, initially empty. Write normal posts in the respective `content/posts/` folder.
- `site.json`: name and institution used on the homepage and in page titles/footers, the last-edited date, topic names and descriptions.
- `assets/style.css`: shared styling.
- `templates/page.html`: shared page structure.

`dist/` is generated output and is replaced during each build. Make edits in the source files above. Your portrait and contact details remain intentional homepage placeholders. Cat Pictures and Work are empty blogs until you add your own posts; there are no mock papers or cat captions.

## First-time GitHub Pages setup

Push the contents of this project to a repository with a `main` branch, including the `.github` folder. In **Settings → Pages**, choose **GitHub Actions** as the source. Run “Deploy to GitHub Pages” from the Actions tab, or push a commit. The workflow installs the two pinned Python dependencies, runs the tests, builds the site, and deploys `dist/`.

The downloaded ZIP also contains a ready-built `dist/` you can open or host directly. Automatic updates from Markdown need the included workflow. The separate private preview does not automatically follow changes in your own GitHub repository.

Run checks locally with `python -m unittest discover -s tests`. Tests exercise publication, drafts, editing/deletion, ordering, section membership, metadata validation, and links under a GitHub project path.

## Design reference

Primary reference: [Patrick O’Neil’s faculty homepage](https://www.cs.umb.edu/~poneil/), displaying “Last updated July 14, 2001.” Its centered identity and portrait, plain sections, blue links, and contact block informed the design. The displayed date is a statement on the live page, not independent proof that every element has remained unchanged since 2001.

## Semiconductors

The semiconductor section starts empty. No sample lessons, exercises, handouts, or slides are published or bundled. The Paul’s Notes-inspired layout remains: compact navigation, a gray background, a wide white reading column, sans-serif text, and blue accents.

### Add a normal blog post

Use `content/posts/chips/`, just like any other topic. Copy `_template.md` to a new Markdown filename, write your post, and change `draft: true` to `draft: false`. It will appear on Semiconductors, the archive, and the homepage’s latest-posts list. Semiconductor posts use the same course styling as the notes.

### Add ordered instructional notes (optional)

If you also want a course-style sequence:

1. Copy `content/courses/semiconductors/_template.md` to your own filename, for example `my-first-lesson.md`.
2. Write your title, summary, and notes. Practice problems are optional: add `<!-- practice -->` followed by exercises only if you want a practice page. Nothing in the underscore-prefixed template is published.
3. Replace `chapters: []` in `content/courses/semiconductors/course.yml` with your chapter and lesson list:

```yaml
title: Semiconductors
description: ""
chapters:
  - title: Your chapter title
    lessons:
      - my-first-lesson
```

Only listed lessons are published, and their order controls the chapter menus and previous/next links. Keep filenames stable to preserve URLs. Add your own introduction in the currently empty `overview.md` if you want one. Unlisted draft files remain visible to anyone who can read your repository.

Individual solutions use native `<details markdown="1">` blocks and work without JavaScript. The page also provides Show All / Hide All controls. Equations can use HTML `<var>`, `<sub>`, and `<sup>`. The optional Print control includes solutions and restores their previous open/closed state afterward.

### Upload your notes and slides

On GitHub, open `assets/files/semiconductors/`, choose **Add file → Upload files**, and commit your PDFs or presentation files. This folder currently contains no instructional files.

For a blog post, link to the upload in Markdown:

```markdown
[My notes (PDF)](assets/files/semiconductors/my-notes.pdf)
[My slides (PDF)](assets/files/semiconductors/my-slides.pdf)
```

For an ordered lesson, you can also add downloads to its YAML header:

```yaml
---
title: Your lesson title
summary: A short description.
downloads:
  - label: Notes (PDF)
    file: assets/files/semiconductors/my-notes.pdf
  - label: Slides (PDF)
    file: assets/files/semiconductors/my-slides.pdf
---
```

Upload the actual files before adding these links. Lesson downloads are automatically listed on the course overview. Every build validates local links, image references, and HTML anchors, including links in ordinary blog posts. There are no hardcoded sample files. Use `assets/`, never generated `dist/`. Your GitHub repository is the editing interface; the public website has no upload or editing form.

The Python files only build the website from your Markdown. GitHub Actions runs them when you commit; readers do not run Python. `assets/course.css` and `assets/course.js` control the semiconductor teaching layout. Ordinary topic blogs keep the minimal academic homepage styling.

## Publication and validation limits

This project is ready for GitHub Pages, but the separately published private Site is not a GitHub Pages deployment. Setting up your own repository and enabling its Pages workflow are still required. No public in-browser editor or CMS is installed: editing means changing Markdown files in GitHub.

The automated tests use isolated content, so adding real posts or lessons does not invalidate tests that expect an empty fixture. The actual build separately validates your real generated pages before replacing the previous output. It checks local files, local anchors, a single main heading, duplicate IDs, and image alt attributes. It does not verify external websites, facts in your writing, visual fidelity, or assistive-technology behavior. Start body headings at `##` because the template supplies `h1`.

Set your name and institution once in `site.json`; `{{name}}` and `{{institution}}` in the homepage reflect them. Replace the other explicit homepage placeholders when ready. Update `site.json`’s `updated` date when editing existing material; post dates alone do not capture revisions to older writing.

The Semiconductors label replaces the former Chip Design label. The existing `chips.html` URL and `content/posts/chips/` folder are retained so links and existing writing continue to work.
