# Advent Puzzles 2026

A 24-door advent calendar of puzzles (maths, logic, chess, football), served by
GitHub Pages at **https://andrei-tm.github.io/advent-26/**.

Plain HTML, CSS and JavaScript. Nothing to build or install.

## Adding puzzles

All the puzzles are in **`questions.yaml`**. The top of that file explains the
format, and days 1–3 are worked examples. In short:

```yaml
  - day: 4
    category: logic          # math, logic, chess or football
    title: A short title

    easy:
      question: |
        The question text. Maths goes between dollar signs: $2 + 2$.
      answers: ["4", "four"]   # any of these counts as right
      hint: An optional clue.

    medium:
      question: |
        White to move. What's the best move?
      fen: 6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1   # optional chess position
      answers: ["Rd8#", "Rd8"]

    hard:
      question: |
        Who is this?
      image: img/my-picture.jpg   # optional picture, put the file in img/
      answers: ["Someone"]
```

Answers ignore capital letters and extra spaces. List every spelling you want
to accept.

You can edit `questions.yaml` straight on github.com (open the file and click
the pencil). The site updates about a minute after you save. If something is
wrong in the file, the page shows a message saying which line.

## Testing a day early

Doors open at midnight (your own time) on their date. To see any day now, add
`?day=N&preview=1` to the address, for example:

https://andrei-tm.github.io/advent-26/?day=2&preview=1

`?preview=1` on its own opens every door on the calendar:
https://andrei-tm.github.io/advent-26/?preview=1

## Running it on your computer

The page loads `questions.yaml` with `fetch`, so double-clicking `index.html`
won't work. Run a tiny web server in this folder instead:

```sh
python3 -m http.server
```

Then open http://localhost:8000.

## Files

| File | What it is |
| --- | --- |
| `questions.yaml` | All the puzzles. This is the file you edit. |
| `index.html` | The page, plus the libraries loaded from CDNs |
| `app.js` | The calendar and answer-checking logic (commented) |
| `style.css` | Colours and layout |
| `img/` | Pictures for questions, and the chess pieces |
| `img/matrix/` | The colour-and-shape grid puzzles for days 12–20 |
| `tools/make_matrices.py` | Optional: redraws the grid puzzles (`python3 tools/make_matrices.py`) and prints each answer letter |

Libraries: [js-yaml](https://github.com/nodeca/js-yaml),
[KaTeX](https://katex.org), [chessboard.js](https://chessboardjs.com) (with
jQuery) and [chess.js](https://github.com/jhlywa/chess.js), all loaded from CDNs.
The chess pieces in `img/pieces/` are Colin M.L. Burnett's set
(CC BY-SA 3.0, via [chessground](https://github.com/lichess-org/chessground)).
