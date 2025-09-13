const BACKEND = (location.hostname === 'localhost') ? 'http://localhost:8000' : (window.__BACKEND_URL || 'http://localhost:8000');

document.getElementById('openStream').onclick = () => {
  window.open('http://localhost:8501', '_blank');
};

document.getElementById('parseBtn').onclick = async () => {
  const text = document.getElementById('presc').value;
  if (!text.trim()) {
    alert("Enter prescription text");
    return;
  }
  try {
    const resp = await fetch(BACKEND + '/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const j = await resp.json();
    document.getElementById('out').textContent = j.plain_text || JSON.stringify(j.structured, null, 2);
  } catch (e) {
    document.getElementById('out').textContent = 'Error: ' + e.toString();
  }
};
