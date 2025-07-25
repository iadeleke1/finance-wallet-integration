function startRitual() {
  document.getElementById('modal').classList.remove('hidden');
  setTimeout(() => {
    document.querySelector('.modal-content').innerHTML = `
      <h2>Descent Complete 🌘</h2>
      <p>Your glyph is ready. Emotional calibration synced.</p>
    `;
  }, 4000);
}
