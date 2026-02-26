(function () {
  const sanitize = (value = '') =>
    value
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');

  const replaceAccents = (value, marker, map) =>
    value.replace(new RegExp(`\\\\${marker}\\{?([A-Za-z])\\}?`, 'g'), (_, letter) => map[letter] || letter);

  const decodeLatex = (input = '') => {
    let value = input;

    const umlaut = { A: 'Ä', O: 'Ö', U: 'Ü', a: 'ä', o: 'ö', u: 'ü', e: 'ë', i: 'ï', y: 'ÿ' };
    const acute = { A: 'Á', E: 'É', I: 'Í', O: 'Ó', U: 'Ú', Y: 'Ý', a: 'á', e: 'é', i: 'í', o: 'ó', u: 'ú', y: 'ý' };
    const grave = { A: 'À', E: 'È', I: 'Ì', O: 'Ò', U: 'Ù', a: 'à', e: 'è', i: 'ì', o: 'ò', u: 'ù' };
    const circumflex = { A: 'Â', E: 'Ê', I: 'Î', O: 'Ô', U: 'Û', a: 'â', e: 'ê', i: 'î', o: 'ô', u: 'û' };
    const tilde = { A: 'Ã', N: 'Ñ', O: 'Õ', a: 'ã', n: 'ñ', o: 'õ' };

    value = replaceAccents(value, '"', umlaut);
    value = replaceAccents(value, "'", acute);
    value = replaceAccents(value, '`', grave);
    value = replaceAccents(value, '\\^', circumflex);
    value = replaceAccents(value, '~', tilde);

    value = value
      .replace(/\{\\aa\}/g, 'å')
      .replace(/\{\\AA\}/g, 'Å')
      .replace(/\\aa\b/g, 'å')
      .replace(/\\AA\b/g, 'Å')
      .replace(/\{\\o\}/g, 'ø')
      .replace(/\{\\O\}/g, 'Ø')
      .replace(/\\o\b/g, 'ø')
      .replace(/\\O\b/g, 'Ø')
      .replace(/\\ss\b/g, 'ß')
      .replace(/\\&/g, '&')
      .replace(/\\#/g, '#')
      .replace(/\\%/g, '%')
      .replace(/\\_/g, '_')
      .replace(/\\\$/g, '$')
      .replace(/\\\{/g, '{')
      .replace(/\\\}/g, '}')
      .replace(/\{\\i\}/g, 'i')
      .replace(/\{\\j\}/g, 'j')
      .replace(/[{}]/g, '');

    return value;
  };

  const normalizeName = (name = '') =>
    name
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^\p{L}\s,]/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim();

  const samePerson = (a, b) => {
    const n1 = normalizeName(a);
    const n2 = normalizeName(b);
    if (!n1 || !n2) return false;
    if (n1 === n2) return true;

    const reorder = (n) => {
      if (!n.includes(',')) return n;
      const [last, first] = n.split(',').map((part) => part.trim());
      return `${first} ${last}`.trim();
    };

    return reorder(n1) === reorder(n2) || reorder(n1) === n2 || reorder(n2) === n1;
  };

  const parseBib = (bibText) => {
    const entries = [];
    const rawEntries = bibText.split('@').map((chunk) => chunk.trim()).filter(Boolean);

    rawEntries.forEach((chunk) => {
      const match = chunk.match(/^(\w+)\s*\{\s*([^,]+),([\s\S]*)\}\s*$/);
      if (!match) return;
      const [, type, key, body] = match;
      const fields = {};
      const fieldRegex = /(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|"[^"]*"),?/g;
      let fieldMatch;
      while ((fieldMatch = fieldRegex.exec(body)) !== null) {
        const field = fieldMatch[1].toLowerCase();
        const rawValue = fieldMatch[2].trim();
        const value = rawValue.replace(/^\{/, '').replace(/\}$/, '').replace(/^"/, '').replace(/"$/, '');
        fields[field] = decodeLatex(value).replace(/\s+/g, ' ').trim();
      }
      entries.push({ key: key.trim(), type: type.toLowerCase(), ...fields });
    });

    return entries;
  };

  const parseExtraYaml = (yamlText) => {
    const map = {};
    let current = null;

    yamlText.split('\n').forEach((line) => {
      const top = line.match(/^([A-Za-z0-9_\-]+):\s*$/);
      if (top) {
        current = top[1];
        map[current] = {};
        return;
      }

      if (!current) return;
      const prop = line.match(/^\s{2}([A-Za-z0-9_\-]+):\s*(.*)$/);
      if (!prop) return;
      const [, name, value] = prop;

      if (name === 'tags') {
        const cleaned = value.replace(/^\[/, '').replace(/\]$/, '');
        map[current][name] = cleaned
          .split(',')
          .map((tag) => tag.trim().replace(/^"|"$/g, ''))
          .filter(Boolean);
      } else {
        map[current][name] = value.trim().replace(/^"|"$/g, '');
      }
    });

    return map;
  };

  const parseAuthors = (authorLine, meToken) => {
    const authors = (authorLine || '')
      .split(' and ')
      .map((name) => name.trim())
      .filter(Boolean);

    return authors
      .map((name) => {
        const highlighted = samePerson(name, meToken) || name.includes('[FULL NAME]');
        return highlighted ? `<strong>${sanitize(name)}</strong>` : sanitize(name);
      })
      .join(', ');
  };

  const extractYear = (entry) => (entry.year || '').replace(/[^0-9]/g, '').slice(0, 4);

  const inferType = (entry) => {
    if (entry.type === 'article') return 'article';
    if (entry.type === 'inproceedings' || entry.type === 'conference') return 'conference';
    if (entry.type === 'misc' || (entry.note || '').toLowerCase().includes('preprint')) return 'preprint';
    return entry.type || 'other';
  };

  const createBadge = (url, label) => {
    if (!url) return '';
    return `<a class="badge-link" href="${sanitize(url)}" target="_blank" rel="noopener">${sanitize(label)}</a>`;
  };

  const createTitle = (title, primaryLink) => {
    const safeTitle = sanitize(title || '[TITLE PLACEHOLDER]');
    if (!primaryLink) return safeTitle;
    return `<a href="${sanitize(primaryLink)}" target="_blank" rel="noopener">${safeTitle}</a>`;
  };

  window.initPublications = async function initPublications(config) {
    const {
      containerId,
      bibUrl,
      extraUrl,
      labels,
      meToken = 'Artur Czeszumski'
    } = config;

    const list = document.getElementById(containerId);
    if (!list) return;

    try {
      const [bibResponse, extraResponse] = await Promise.all([fetch(bibUrl), fetch(extraUrl)]);
      const bibText = await bibResponse.text();
      const extraText = await extraResponse.text();

      const entries = parseBib(bibText).sort((a, b) => Number(extractYear(b)) - Number(extractYear(a)));
      const extras = parseExtraYaml(extraText);

      const html = entries
        .map((entry) => {
          const year = extractYear(entry) || 'n/a';
          const type = inferType(entry);
          const extra = extras[entry.key] || {};
          const tags = extra.tags || (entry.keywords || '').split(',').map((v) => v.trim()).filter(Boolean);
          const venue = entry.journal || entry.booktitle || entry.note || '';

          const doiLink = entry.doi ? `https://doi.org/${entry.doi}` : '';
          const primaryLink = extra.link || doiLink || extra.pdf || extra.scholar || extra.code || '';

          return `
            <article class="pub-item reveal" data-year="${sanitize(year)}" data-type="${sanitize(type)}" data-tags="${sanitize(tags.join(', '))}">
              <div class="pub-meta">${sanitize(venue)} · ${sanitize(year)} · ${sanitize(type)}</div>
              <h3 class="pub-title">${createTitle(entry.title, primaryLink)}</h3>
              <div>${parseAuthors(entry.author, meToken)}</div>
              <div class="pub-actions">
                ${createBadge(extra.link, 'Link')}
                ${createBadge(extra.scholar, 'Scholar')}
                ${createBadge(doiLink, 'DOI')}
                ${createBadge(extra.pdf, 'PDF')}
                ${createBadge(extra.code, 'Code')}
              </div>
            </article>
          `;
        })
        .join('');

      list.innerHTML = html;

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('in-view');
        });
      }, { threshold: 0.08 });
      list.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
    } catch (error) {
      list.innerHTML = `<p>${sanitize(labels.errorText)}</p>`;
    }
  };
})();
