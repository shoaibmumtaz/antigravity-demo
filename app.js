document.addEventListener('DOMContentLoaded', () => {
  const button = document.getElementById('counter-btn');
  let count = 0;

  if (button) {
    button.addEventListener('click', () => {
      count++;
      button.textContent = `Clicks: ${count}`;
      button.style.transform = 'scale(0.96)';
      setTimeout(() => {
        button.style.transform = '';
      }, 100);
    });
  }
});

