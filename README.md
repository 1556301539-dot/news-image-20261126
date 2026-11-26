# The World in One Page — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/1556301539-dot/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/1556301539-dot/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws one front page summing up the world's news of
Thursday 26 November 2026, for the make.fun bounty
[news-image-20261126](https://make.fun/bounty/news-image-20261126).

## The image

30 stories, 6 regions, 12 fields. Three big scenes — tankers hit by
mines in the Strait of Hormuz, the Macy's Thanksgiving parade called
off by a nor'easter for the first time in 100 years, and Kim Jong Un
vowing to expand North Korea's nuclear weapons — plus ten small
scenes, a world map with numbered dots, a six-number strip, a UTC
timeline built only from real clock times, and a boxed DATE CHECK
that names the old news we left out.

Every story carries a credibility label — OFFICIAL, REPORTED or
CLAIM — with a legend under the masthead. Nothing is presented as
fact that was only claimed, and nothing from another day is passed
off as today's news. All 30 stories are sourced in `SOURCES.md`.

## How it is built

`render.py` is a deterministic Pillow program: run it twice and the
bytes are identical. It draws the 1024×1024 page — masthead, scenes,
map, briefs — with no network, no fonts beyond the system DejaVu
faces, and no image files. `main.py` (standard library only) copies
`entry.png` to the grader's output directory.

```
python3 render.py          # draws entry.png (1024x1024, < 1 MiB)
python3 -P -s main.py      # copies entry.png to /output/entry.png
```

## Files

- `render.py` — the drawing program
- `main.py` — the entrypoint (stdlib copy program)
- `entry.png` — the finished front page
- `SOURCES.md` — all 30 stories, their sources, and the DATE CHECK
- `BUILD_REPORT.md` — how it was built and checked
- `LICENSE` — MIT
