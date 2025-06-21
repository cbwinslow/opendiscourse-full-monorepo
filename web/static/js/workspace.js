function loadHistory(){
  const list = document.getElementById('history');
  list.innerHTML = '';
  const items = JSON.parse(localStorage.getItem('queries') || '[]');
  items.forEach((q,i)=>{
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#';
    a.textContent = q;
    a.onclick = () => { document.getElementById('query').value = q; return false; };
    li.appendChild(a);
    list.appendChild(li);
  });
}

async function runQuery(){
  const q = document.getElementById('query').value;
  const resp = await fetch('/api/rag', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  const json = await resp.json();
  document.getElementById('result').textContent = json.answer || JSON.stringify(json);
}

function saveQuery(){
  const q = document.getElementById('query').value;
  const items = JSON.parse(localStorage.getItem('queries') || '[]');
  items.push(q);
  localStorage.setItem('queries', JSON.stringify(items));
  loadHistory();
}

loadHistory();
