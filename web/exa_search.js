const apiKey = localStorage.getItem('EXA_API_KEY') || '';
const queryInput = document.getElementById('query');
const numResultsInput = document.getElementById('numResults');
const matchInput = document.getElementById('matchThreshold');
const resultsDiv = document.getElementById('results');
const ingestBtn = document.getElementById('ingestBtn');

function buildQuery() {
    const query = queryInput.value;
    const numResults = parseInt(numResultsInput.value, 10) || 10;
    const match = parseFloat(matchInput.value) || 0.7;
    return { query, num_results: numResults, match_threshold: match };
}

// 1. Extract your language templates into a single map:
const langTemplates = {
  json: s => s,
  curl: s => `curl -X POST https://api.exa.ai/search \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer ${apiKey}' \
-d '${s}'`,
  python: s => `import requests
headers = {'Authorization': 'Bearer ${apiKey}'}
resp = requests.post('https://api.exa.ai/search', json=${s})
print(resp.json())`,
  ts: s => `fetch('https://api.exa.ai/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ${apiKey}'
  },
  body: JSON.stringify(${s})
})`,
  go: s => `package main
import ("bytes"; "net/http")
func main() {
  http.Post("https://api.exa.ai/search", "application/json", bytes.NewBuffer([]byte('${s}')))
}`,
  rust: s => `reqwest::Client::new()
  .post("https://api.exa.ai/search")
  .bearer_auth("${apiKey}")
  .json(&${s})
  .send()
  .await?;`
};

// 2. In updateQueryStrings(), iterate the map instead of hard-coding each block:
function updateQueryStrings() {
  const params = buildQuery();
  const jsonStr = JSON.stringify(params, null, 2);
  Object.entries(langTemplates).forEach(([lang, tmpl]) => {
    document.getElementById(lang).textContent = tmpl(jsonStr);
  });
}

// 3. Batch-wire inputs to the same handler:
[ queryInput, numResultsInput, matchInput ]
  .forEach(el =>
    ['input','change'].forEach(evt =>
      el.addEventListener(evt, updateQueryStrings)
    )
  );

// 4. (Optionally) Cache your tab buttons & contents:
const tabs = {
  buttons: document.querySelectorAll('.tab-buttons button'),
  contents: document.querySelectorAll('.tab-content')
};
tabs.buttons.forEach(btn =>
  btn.addEventListener('click', () => {
    tabs.contents.forEach(c => c.classList.remove('active'));
    document.getElementById(btn.dataset.lang).classList.add('active');
  })
);
    const params = buildQuery();
    const jsonStr = JSON.stringify(params, null, 2);
    document.getElementById('json').textContent = jsonStr;
    document.getElementById('curl').textContent =
        `curl -X POST https://api.exa.ai/search -H 'Content-Type: application/json' -H 'Authorization: Bearer ${apiKey}' -d '${jsonStr}'`;
    document.getElementById('python').textContent =
`import requests
headers = {'Authorization': 'Bearer ${apiKey}'}
resp = requests.post('https://api.exa.ai/search', json=${jsonStr})
print(resp.json())`;
    document.getElementById('ts').textContent =
`fetch('https://api.exa.ai/search', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ${apiKey}' }, body: JSON.stringify(${jsonStr}) })`;
    document.getElementById('go').textContent =
`package main
import ("bytes"; "net/http")
func main() { http.Post("https://api.exa.ai/search", "application/json", bytes.NewBuffer([]byte('${jsonStr}'))) }`;
    document.getElementById('rust').textContent =
`reqwest::Client::new().post("https://api.exa.ai/search").bearer_auth("${apiKey}").json(&${jsonStr}).send().await?;`;
}

function showTab(lang) {
    document.querySelectorAll('.tab-content').forEach(div => div.classList.remove('active'));
    document.getElementById(lang).classList.add('active');
}

document.querySelectorAll('.tab-buttons button').forEach(btn => {
    btn.addEventListener('click', () => showTab(btn.dataset.lang));
});

['input', 'change'].forEach(evt => {
    queryInput.addEventListener(evt, updateQueryStrings);
    numResultsInput.addEventListener(evt, updateQueryStrings);
    matchInput.addEventListener(evt, updateQueryStrings);
});

async function runSearch() {
    const payload = buildQuery();
    updateQueryStrings();
    const resp = await fetch('https://api.exa.ai/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(payload)
    });
    const data = await resp.json();
    displayResults(data.results || []);
}

function displayResults(results) {
    resultsDiv.innerHTML = '';
    results.forEach((r, idx) => {
        const div = document.createElement('div');
        div.className = 'result';
        div.innerHTML = `<input type="checkbox" class="selectDoc" data-url="${r.url}"> <a href="${r.url}" target="_blank">${r.title || r.url}</a> (score: ${r.score})`;
        resultsDiv.appendChild(div);
    });
}

async function ingestSelected() {
    const urls = Array.from(document.querySelectorAll('.selectDoc:checked')).map(cb => cb.dataset.url);
    if (urls.length === 0) return alert('No documents selected.');
    // Placeholder: send to backend ingestion endpoint if available
    console.log('Ingesting', urls);
    alert('Would ingest ' + urls.length + ' documents');
}

searchBtn.addEventListener('click', runSearch);
ingestBtn.addEventListener('click', ingestSelected);

updateQueryStrings();
showTab('json');
