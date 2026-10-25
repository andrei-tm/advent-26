/*
 * Advent Puzzles: all the site logic lives in this one file.
 *
 * How it works:
 *   1. Load questions.yaml and turn it into a JavaScript object (js-yaml).
 *   2. Look at the address bar:
 *        index.html                 → show the calendar of 24 doors
 *        index.html?day=5           → show the puzzles for day 5
 *        index.html?day=5&preview=1 → same, but ignore the date (for testing)
 *   3. Doors unlock at local midnight on their date in December.
 *   4. Solved questions are remembered in localStorage (on this device only).
 *
 * You shouldn't need to edit this file to add puzzles. Edit questions.yaml.
 */

// ---------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------

const LEVELS = ['easy', 'medium', 'hard'];

// How each category looks. Add a line here to invent a new category.
const CATEGORIES = {
  math:     { label: 'Maths',    icon: '➗' },
  logic:    { label: 'Logic',    icon: '🧩' },
  chess:    { label: 'Chess',    icon: '♞' },
  football: { label: 'Football', icon: '⚽' },
};

// The order the doors appear on the calendar (mixed up, like a real one).
const DOOR_ORDER = [
  7, 15, 2, 21, 11, 18,
  4, 24, 9, 13, 1, 20,
  16, 6, 23, 3, 12, 19,
  10, 22, 5, 17, 8, 14,
];

// Where the chess piece pictures live (in this repo).
const PIECE_THEME = 'img/pieces/{piece}.svg';

// ---------------------------------------------------------------------
// Reading the address bar
// ---------------------------------------------------------------------

const params = new URLSearchParams(window.location.search);
const PREVIEW = params.get('preview') === '1';
const DAY_PARAM = params.get('day');

// Build a link to a day (or to the calendar if day is null),
// keeping preview mode switched on if it already is.
function linkTo(day) {
  const p = new URLSearchParams();
  if (day) p.set('day', day);
  if (PREVIEW) p.set('preview', '1');
  const query = p.toString();
  return query ? '?' + query : './';
}

// ---------------------------------------------------------------------
// Saving progress (localStorage)
// ---------------------------------------------------------------------
// We store one object like { "2026-d3-easy": true, ... }.
// localStorage can be missing or blocked (private windows), so every
// access is wrapped in try/catch and the site still works without it.

const STORAGE_KEY = 'advent-puzzles-solved';

function loadSolved() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch (e) {
    return {};
  }
}

function saveSolved(solved) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(solved));
  } catch (e) {
    // Nothing we can do. Progress just won't be remembered.
  }
}

function solvedKey(year, day, level) {
  return `${year}-d${day}-${level}`;
}

function isSolved(year, day, level) {
  return loadSolved()[solvedKey(year, day, level)] === true;
}

function markSolved(year, day, level) {
  const solved = loadSolved();
  solved[solvedKey(year, day, level)] = true;
  saveSolved(solved);
}

// ---------------------------------------------------------------------
// Dates
// ---------------------------------------------------------------------

// Door N opens at midnight (the player's own time zone) on N December.
function unlockDate(year, day) {
  return new Date(year, 11, day); // months count from 0, so 11 = December
}

function isUnlocked(year, day) {
  return PREVIEW || new Date() >= unlockDate(year, day);
}

function isToday(year, day) {
  const now = new Date();
  return now.getFullYear() === year && now.getMonth() === 11 && now.getDate() === day;
}

// ---------------------------------------------------------------------
// Checking answers
// ---------------------------------------------------------------------

// Make an answer easy to compare: lower case, single spaces, no
// spaces at the ends. "  Real   MADRID " becomes "real madrid".
function normalise(text) {
  return String(text).toLowerCase().replace(/\s+/g, ' ').trim();
}

function isCorrect(guess, acceptedAnswers) {
  const g = normalise(guess);
  return g !== '' && acceptedAnswers.some((a) => normalise(a) === g);
}

// ---------------------------------------------------------------------
// Small helpers for building the page
// ---------------------------------------------------------------------

// Create an element: el('p', 'my-class', 'some text')
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// Turn $...$ and $$...$$ inside an element into nice maths (KaTeX).
function renderMath(node) {
  if (!window.renderMathInElement) return; // KaTeX failed to load. Show the raw text.
  window.renderMathInElement(node, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '$', right: '$', display: false },
    ],
    throwOnError: false, // a typo in the maths shows in red instead of breaking the page
  });
}

// Show a friendly error message in place of the page.
function showError(title, details) {
  const app = document.getElementById('app');
  app.replaceChildren();
  const box = el('div', 'error-box');
  box.append(el('h2', '', title));
  if (details) box.append(el('pre', '', details));
  app.append(box);
}

function formatDate(date) {
  return date.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' });
}

// ---------------------------------------------------------------------
// The calendar page (24 doors)
// ---------------------------------------------------------------------

function renderCalendar(data) {
  const app = document.getElementById('app');
  app.replaceChildren();

  // Before 1 December, say how long there is to wait.
  const firstDoor = unlockDate(data.year, 1);
  if (!PREVIEW && new Date() < firstDoor) {
    const daysLeft = Math.ceil((firstDoor - new Date()) / 86400000);
    app.append(el('p', 'countdown',
      `The first door opens in ${daysLeft} day${daysLeft === 1 ? '' : 's'}.`));
  }

  const grid = el('div', 'calendar');

  for (const day of DOOR_ORDER) {
    const entry = data.byDay[day];
    const open = isUnlocked(data.year, day);

    // Open doors are links; locked doors are plain boxes.
    const door = el(open ? 'a' : 'div', 'door');
    if (open) door.href = linkTo(day);
    if (!open) door.classList.add('door--locked');
    if (isToday(data.year, day)) door.classList.add('door--today');
    if (open && !entry) door.classList.add('door--empty');
    if (entry && CATEGORIES[entry.category]) door.dataset.category = entry.category;

    door.append(el('span', 'door-number', day));

    if (!open) {
      door.append(el('span', 'door-status', '🔒'));
      door.setAttribute('aria-label', `Day ${day}, locked until ${formatDate(unlockDate(data.year, day))}`);
    } else if (!entry) {
      door.append(el('span', 'door-status', 'No puzzle yet'));
    } else {
      const cat = CATEGORIES[entry.category];
      if (cat) door.append(el('span', 'door-icon', cat.icon));

      // One star per level solved.
      const stars = el('span', 'door-stars');
      let solvedCount = 0;
      for (const level of LEVELS) {
        if (!entry[level]) continue;
        const done = isSolved(data.year, day, level);
        if (done) solvedCount++;
        stars.append(el('span', done ? 'star star--done' : 'star', done ? '★' : '☆'));
      }
      door.append(stars);
      door.setAttribute('aria-label', `Day ${day}, ${solvedCount} solved`);
    }

    grid.append(door);
  }

  app.append(grid);
}

// ---------------------------------------------------------------------
// A single day's page (the three questions)
// ---------------------------------------------------------------------

function renderDay(data, day) {
  const app = document.getElementById('app');
  app.replaceChildren();

  const entry = data.byDay[day];

  // Navigation: back to calendar, previous and next day.
  const nav = el('nav', 'day-nav');
  const back = el('a', 'button button--ghost', '← All doors');
  back.href = linkTo(null);
  nav.append(back);
  const arrows = el('span', 'day-arrows');
  if (day > 1) {
    const prev = el('a', 'button button--ghost', '‹ Day ' + (day - 1));
    prev.href = linkTo(day - 1);
    arrows.append(prev);
  }
  if (day < 24) {
    const next = el('a', 'button button--ghost', 'Day ' + (day + 1) + ' ›');
    next.href = linkTo(day + 1);
    arrows.append(next);
  }
  nav.append(arrows);
  app.append(nav);

  // Not open yet?
  if (!isUnlocked(data.year, day)) {
    const box = el('div', 'locked-box');
    box.append(el('p', 'locked-icon', '🔒'));
    box.append(el('h1', '', `Door ${day} is still closed`));
    box.append(el('p', '', `It opens on ${formatDate(unlockDate(data.year, day))}. No peeking!`));
    app.append(box);
    return;
  }

  // Open, but nobody has written the puzzle yet.
  if (!entry) {
    const box = el('div', 'locked-box');
    box.append(el('h1', '', `Day ${day}`));
    box.append(el('p', '', 'There is no puzzle for this day yet. Add one to questions.yaml.'));
    app.append(box);
    return;
  }

  // Heading
  const cat = CATEGORIES[entry.category] || { label: entry.category || 'Puzzle', icon: '🎁' };
  const header = el('header', 'day-header');
  header.dataset.category = entry.category;
  header.append(el('p', 'day-badge', `${cat.icon} ${cat.label}`));
  header.append(el('h1', 'day-title', `Day ${day}${entry.title ? ': ' + entry.title : ''}`));
  header.append(el('p', 'day-intro', 'Pick a level, or try all three!'));
  app.append(header);

  // One card per level
  const levels = el('div', 'levels');
  for (const level of LEVELS) {
    if (entry[level]) levels.append(renderLevel(data, day, level, entry[level]));
  }
  app.append(levels);

  // A cheer when every level of the day is solved
  const cheer = el('p', 'day-cheer', '🎉 You solved every level today! Brilliant!');
  cheer.hidden = !allSolved(data, day);
  app.append(cheer);
}

function allSolved(data, day) {
  const entry = data.byDay[day];
  return LEVELS.filter((l) => entry[l]).every((l) => isSolved(data.year, day, l));
}

// Build the card for one level (easy, medium or hard) of a day.
function renderLevel(data, day, level, q) {
  const card = el('section', `level level--${level}`);
  if (isSolved(data.year, day, level)) card.classList.add('level--solved');

  const title = el('h2', 'level-title');
  title.append(el('span', 'level-name', level[0].toUpperCase() + level.slice(1)));
  title.append(el('span', 'level-tick', '✓ Solved'));
  card.append(title);

  // Spot mistakes in questions.yaml and explain them on the page.
  const problems = [];
  if (!q.question) problems.push('it has no "question:"');
  if (!Array.isArray(q.answers) || q.answers.length === 0) problems.push('it has no "answers:" list');
  if (problems.length) {
    card.append(el('p', 'yaml-problem',
      `Day ${day} ${level} needs fixing in questions.yaml: ${problems.join(' and ')}.`));
    return card;
  }

  // The question text (maths is rendered by KaTeX)
  const question = el('div', 'question', String(q.question).trim());
  card.append(question);
  renderMath(question);

  // Optional chess board
  if (q.fen) card.append(renderBoard(String(q.fen).trim()));

  // Optional picture
  if (q.image) {
    const img = el('img', 'question-image');
    img.src = q.image;
    img.alt = 'Picture for this question';
    img.loading = 'lazy';
    card.append(img);
  }

  // Answer box
  const form = el('form', 'answer-form');
  const inputId = `answer-${day}-${level}`;
  const label = el('label', 'visually-hidden', 'Your answer');
  label.htmlFor = inputId;
  const input = el('input', 'answer-input');
  input.id = inputId;
  input.type = 'text';
  input.autocomplete = 'off';
  input.autocapitalize = 'off';
  input.spellcheck = false;
  input.placeholder = 'Your answer';
  const button = el('button', 'button', 'Check');
  button.type = 'submit';
  form.append(label, input, button);
  card.append(form);

  const feedback = el('p', 'feedback');
  feedback.setAttribute('aria-live', 'polite');
  card.append(feedback);

  form.addEventListener('submit', (event) => {
    event.preventDefault(); // stop the page from reloading
    if (input.value.trim() === '') {
      input.focus();
      return;
    }
    if (isCorrect(input.value, q.answers)) {
      markSolved(data.year, day, level);
      card.classList.add('level--solved');
      feedback.textContent = 'Correct! Well done! 🎉';
      feedback.className = 'feedback feedback--right';
      document.querySelector('.day-cheer').hidden = !allSolved(data, day);
    } else {
      feedback.textContent = 'Not quite. Have another go!';
      feedback.className = 'feedback feedback--wrong';
      // Restart the little shake animation
      card.classList.remove('shake');
      void card.offsetWidth;
      card.classList.add('shake');
    }
  });

  // Optional hint, hidden until the player asks for it
  if (q.hint) {
    const details = el('details', 'hint');
    details.append(el('summary', '', 'Need a hint?'));
    const hintText = el('div', 'hint-text', String(q.hint).trim());
    details.append(hintText);
    renderMath(hintText);
    card.append(details);
  }

  return card;
}

// ---------------------------------------------------------------------
// Chess boards
// ---------------------------------------------------------------------

// Every board on the page, so we can resize them when the window changes.
const boards = [];

function renderBoard(fen) {
  const wrap = el('div', 'board-wrap');

  if (!window.Chess || !window.Chessboard) {
    wrap.append(el('p', 'yaml-problem', 'The chess libraries did not load. Check your internet connection.'));
    return wrap;
  }

  // chess.js checks the FEN is a legal position description.
  const check = new Chess().validate_fen(fen);
  if (!check.valid) {
    wrap.append(el('p', 'yaml-problem', `This chess position (fen) has a mistake: ${check.error}\n${fen}`));
    return wrap;
  }

  const game = new Chess(fen);
  const whiteToMove = game.turn() === 'w';

  const boardDiv = el('div', 'board');
  wrap.append(boardDiv);
  wrap.append(el('p', 'to-move', whiteToMove ? '⚪ White to move' : '⚫ Black to move'));

  // chessboard.js needs the element to be on the page before drawing,
  // so we draw it right after this function returns.
  requestAnimationFrame(() => {
    boards.push(Chessboard(boardDiv, {
      position: fen,
      orientation: whiteToMove ? 'white' : 'black', // show it from the mover's side
      pieceTheme: PIECE_THEME,
      showNotation: true,
    }));
  });

  return wrap;
}

window.addEventListener('resize', () => boards.forEach((b) => b.resize()));

// ---------------------------------------------------------------------
// Loading questions.yaml and starting up
// ---------------------------------------------------------------------

async function loadQuestions() {
  // "no-cache" makes sure edits to questions.yaml show up straight away.
  const response = await fetch('questions.yaml', { cache: 'no-cache' });
  if (!response.ok) throw new Error(`Could not load questions.yaml (${response.status})`);
  const text = await response.text();

  let raw;
  try {
    raw = jsyaml.load(text);
  } catch (e) {
    // js-yaml's message says which line the problem is on.
    const err = new Error('There is a typo in questions.yaml');
    err.details = e.message;
    throw err;
  }

  const data = {
    year: Number(raw && raw.year) || new Date().getFullYear(),
    byDay: {}, // day number → that day's entry
  };
  for (const entry of (raw && raw.days) || []) {
    const day = Number(entry && entry.day);
    if (day >= 1 && day <= 24) data.byDay[day] = entry;
  }
  return data;
}

async function start() {
  if (PREVIEW) document.getElementById('preview-banner').hidden = false;

  let data;
  try {
    data = await loadQuestions();
  } catch (e) {
    showError(e.message, e.details ||
      (window.location.protocol === 'file:'
        ? 'Open the site through a web server (see README.md), not by double-clicking index.html.'
        : String(e)));
    return;
  }

  if (DAY_PARAM === null) {
    renderCalendar(data);
    return;
  }

  const day = Number(DAY_PARAM);
  if (!Number.isInteger(day) || day < 1 || day > 24) {
    showError('There is no such door', 'Pick a day from 1 to 24.');
    return;
  }
  document.title = `Day ${day} · Advent Puzzles ${data.year}`;
  renderDay(data, day);
}

start();
