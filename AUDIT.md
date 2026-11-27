# Site audit — 26 November 2026

The most serious defect was that adding real content could break the publishing workflow. Tests copied the author's live content and then assumed that no published posts or lessons existed. This was reproduced with one valid post: a test failed with `AssertionError: 1 != 0`. It is now fixed.

**Overall verdict:** the previous version was an inadequately tested starter, despite passing its original checks. The revised version passes the authoring workflow and generated-page checks described below. It is not yet a verified public GitHub Pages deployment. A numerical grade would imply an assessment rubric that has not been specified.

## Ranked findings

| Severity | Evidence and reasoning failure | Consequence | Correction / status |
| --- | --- | --- | --- |
| Fatal to the publishing workflow | Tests copied `content/` and asserted `self.assertEqual(build(self.root),0)`. This conflated an empty test fixture with the actual author's website. | A legitimate first post could make GitHub Actions fail before deployment. | Fixed. Tests create isolated content; real content is checked separately by the build. A populated-copy simulation with posts, a lesson, and an upload passed. |
| Significant | The README said: `The display name “DB AM” is retained exactly as requested.` This was literal transcription without interpreting the vintage-car context. | The public navigation used unexplained shorthand rather than a meaningful category. | Fixed to **Aston Martin — DB Series**. The established `db-am.html` URL and Markdown folder remain stable. |
| Significant | Work contained `[Paper or essay title]` and Cat Pictures contained `[Cat photo 01]` above their blog feeds. They also required editing HTML, while the stated writing workflow was Markdown. | The sections looked populated by mock entries and had two different authoring methods. | Removed the mock work entries and cat gallery. Work and Cat Pictures are empty blogs with optional Markdown introductions. Resume is now editable in Markdown too. |
| Significant | The lesson parser required both notes and practice: `len(body) != 2 or not all(part.strip() for part in body)`. | Publishing notes or slides required inventing exercises to satisfy the implementation. | Fixed. A notes-only lesson is valid. Practice pages and links appear only for lessons with exercises, and their previous/next links skip lessons without exercises. |
| Significant | The course overview used `course=True`, while semiconductor blog posts used the ordinary page renderer. | Following a semiconductor post silently changed from the requested course style to the generic academic style. | Fixed. Semiconductor posts now use the same course shell, navigation, and stylesheet. |
| Significant | Local-link checks ran on test content; ordinary posts were not validated against their actual uploaded files during publication. | A mistyped file path or anchor could be published successfully. | Fixed. Every build validates the actual generated pages before replacing the previous output. Missing local files and anchors now fail with the affected page and link. |
| Cosmetic, with an editing consequence | `site.json` supplied identity to titles and footers, but the homepage separately hardcoded `[Your Name]` and `[Institution]`. | Updating identity in one place could leave conflicting text elsewhere. | Fixed. The homepage now reads the same name and institution values. |
| Cosmetic | The homepage introduction mentioned only the resume, selected work, and cat pictures after the site had expanded substantially. | The introduction no longer described the navigation beneath it. | Updated to describe work, notes, photographs, and the listed subjects. |

## Earlier judgment failures

- **Insufficient visual comparison:** the initial claim to follow Paul's Notes rested on generic course features. The large banner, serif body text, and permanent sidebar did not match the inspected reference. The later revision corrected those structural differences using the actual reference, with the requested blue accents. Automated checks do not establish visual fidelity.
- **Unnecessary content creation:** the initial semiconductor implementation supplied lessons and sample PDFs when the core request was a reusable website structure. Those files were removed at your direction and remain absent. No replacement semiconductor subject matter was added in this audit.
- **Inadequate acceptance criteria:** reporting the number of passing tests did not establish that the website met the brief, that an author could publish real material, or that it was hosted on GitHub Pages. These are separate checks, and they should have been described separately.

## Intentional features, not discrepancies

- The name, portrait, affiliation, and contact placeholders were explicitly requested. No personal facts or photographs have been invented.
- Bristol, Aston Martin — DB Series, and Hongqi belong under Vintage Cars. Each has its own blog, and the parent page aggregates their posts without duplicating them in the global archive.
- “Fine Firearms,” “Vintage Boats,” and the other user-supplied topic names have been retained. They have no invented articles.
- The semiconductor area remains empty until you add content. The editable source template is not published.
- The general academic theme and the semiconductor course theme differ intentionally because the latter received a separate design request.
- “Editable” currently means Markdown editing through the repository. A public in-browser editor or CMS was never implemented; the README now makes that boundary explicit.

## Verification

- **21 automated tests passed.** These cover post publication and drafts, updates and deletion, grouping and ordering, GitHub project-path links, metadata, identity consistency, Markdown introductions, semiconductor styling, optional practice, and validation failures preserving existing output.
- **24 real generated HTML pages validated.** The build checks local link targets, HTML anchors, one main heading per page, duplicate IDs, and image alt attributes.
- **Author-content simulation passed.** In a temporary project copy, two real posts, a notes-only lesson, and an uploaded file were added. The full test suite and build passed, the vintage-car post appeared in its subsection and parent feed, and the semiconductor post retained course styling. This test content was not published.
- The generated site and source were checked for old sample downloads, sample semiconductor material, mock work entries, and mock cat captions; none remained.
- **Visual browser review remains unverified.** The managed preview service returned `preview relay unavailable`. The private hosted site also requires sign-in in the review browser. No screenshot-based acceptance claim is made.
- **GitHub Pages publication remains unverified.** The live URL is a private Sites deployment. The repository files and workflow are prepared for GitHub Pages, but no user GitHub repository has been connected or deployed in this session. The GitHub-hosted workflow itself was not executed here.

## Strengths and remaining priorities

The static architecture is small, has no database or runtime Python requirement for readers, and keeps content in portable Markdown. Stable existing URLs were preserved. Empty states now reflect the absence of authored content honestly.

1. Complete visual acceptance on desktop and mobile when a working preview is available. Review readability, menu wrapping, keyboard use, and the resemblance to the chosen reference.
2. Connect the intended GitHub repository, enable Pages through GitHub Actions, and verify the resulting public URL. The private preview does not synchronize with a separate GitHub repository automatically.
3. Replace the intentional homepage and resume placeholders and add your own posts, images, notes, and slides. The README specifies the source locations.
4. Keep the `updated` date current when revising older material. It is an author-maintained date; publication dates alone do not detect edits to old writing.

The principal process gaps were interpreting the brief, distinguishing content from structure, testing the author's real workflow, and separating functional tests from visual acceptance. The corrections above address the concrete failures without inventing new subject matter or new site sections.
