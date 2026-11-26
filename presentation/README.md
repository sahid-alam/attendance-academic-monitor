# Presentation

S4 / Madiha Iram coordinates the deck; all four roles speak.

- [Editable PowerPoint](AAM_PRESENTATION.pptx)
- [Presentation PDF](AAM_PRESENTATION.pdf)
- [Slide text and speaker notes](SLIDES.md)
- [Rehearsal checklist, timing and record](REHEARSAL.md)
- [Canonical slide source](slides.json)

Rebuild artifacts from the repository root:

```bash
.venv/bin/python -m pip install -r tools/submission_requirements.txt
.venv/bin/python tools/build_submission.py
```

The script also generates the report PDF and planning PNGs. It embeds Open Sans when installed at `/usr/share/fonts/truetype/open-sans`; other systems use the available fallback fonts. Application dependencies stay in `src/requirements.txt`.

AAM-35 supplies the deck; AAM-37 requires an actual team rehearsal. The planned 600-second run is not a completed rehearsal.
