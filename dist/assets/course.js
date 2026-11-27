// Progressive enhancement: individual solutions also work without JavaScript.
const solutions = [...document.querySelectorAll('.lesson-body details')];
const controls = document.querySelector('.solution-controls');
if (controls && solutions.length) controls.hidden = false;
document.querySelectorAll('[data-solutions]').forEach(button => {
  button.addEventListener('click', () => {
    solutions.forEach(solution => { solution.open = button.dataset.solutions === 'show'; });
  });
});
document.querySelectorAll('[data-print]').forEach(button => {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
});
const menus = [...document.querySelectorAll('.chapter-menu')];
menus.forEach(menu => menu.addEventListener('toggle', () => {
  if (menu.open) menus.forEach(other => { if (other !== menu) other.open = false; });
}));
document.addEventListener('click', event => {
  menus.forEach(menu => { if (!menu.contains(event.target)) menu.open = false; });
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') menus.forEach(menu => {
    if (menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
  });
});
let printState = [];
window.addEventListener('beforeprint', () => {
  printState = solutions.map(solution => solution.open);
  solutions.forEach(solution => { solution.open = true; });
});
window.addEventListener('afterprint', () => {
  solutions.forEach((solution, index) => { solution.open = printState[index] ?? false; });
});
