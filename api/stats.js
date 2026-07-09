const https = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const appId = req.query.id;
  if (!appId) return res.status(400).json({ error: 'Missing ?id= parameter' });

  try {
    const data = await new Promise((resolve, reject) => {
      const url = `https://flathub.org/api/v2/stats/${appId}`;
      https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (resp) => {
        let body = '';
        resp.on('data', c => body += c);
        resp.on('end', () => {
          if (resp.statusCode !== 200) return reject(new Error(`Flathub ${resp.statusCode}`));
          resolve(JSON.parse(body));
        });
      }).on('error', reject);
    });

    res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate');
    res.status(200).json(data);
  } catch (e) {
    res.status(502).json({ error: e.message });
  }
};
