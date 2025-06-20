const express = require('express');
const fs = require('fs');
const { execFile } = require('child_process');

const router = express.Router();
const scriptsDir = `${__dirname}/../../scripts`;

router.get('/', (req, res) => {
  fs.readdir(scriptsDir, (err, files) => {
    if (err) return res.status(500).json({ error: err.message });
    const pyFiles = files.filter(f => f.endsWith('.py'));
    res.json(pyFiles);
  });
});

router.post('/run', (req, res) => {
  const { script, args = [] } = req.body;
  const scriptPath = `${scriptsDir}/${script}`;
  if (!fs.existsSync(scriptPath)) return res.status(404).send('Script not found');
  execFile('python', [scriptPath, ...args], { maxBuffer: 1024 * 500 }, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(stderr || error.message);
    }
    res.send(stdout);
  });
});

module.exports = router;
