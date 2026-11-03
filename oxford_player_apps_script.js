/**
 * GOOGLE APPS SCRIPT: PEMUTAR AUDIO OXFORD 3000 LANGSUNG DI GOOGLE SHEET
 * 
 * FITUR UTAMA:
 * 1. Memutar file audio INTERNAL dari Google Drive langsung di dalam Google Sheet tanpa membuka tab baru!
 * 2. Fallback otomatis & tombol manual ke www.oxfordlearnersdictionaries.com (jika diklik, TIDAK membuka tab baru, tapi langsung diputar di dalam Google Sheet!).
 * 3. Auto-play saat baris diklik/dipilih di spreadsheet (zero clicks, zero new tabs).
 * 4. Pengatur kecepatan suara (0.8x, 1.0x, 1.2x).
 * 5. Kartu kosa kata interaktif (Level CEFR, Arti Bahasa Indonesia, Fonetik IPA UK/US, Contoh Kalimat).
 * 
 * CARA MEMASANG (30 Detik):
 * 1. Buka spreadsheet Google Sheet Anda.
 * 2. Klik menu: Extensions > Apps Script (Ekstensi > Apps Script).
 * 3. Hapus kode default (jika ada), lalu PASTE SELURUH KODE INI.
 * 4. Klik ikon Simpan (Disket) atau tekan Ctrl + S.
 * 5. Kembali ke Google Sheet Anda, refresh browser (tekan F5).
 * 6. Klik menu baru di atas: "🔊 Oxford Audio" > "▶ Buka Pemutar Audio (Sidebar)". Selesai!
 */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🔊 Oxford Audio')
    .addItem('▶ Buka Pemutar Audio (Sidebar)', 'showAudioSidebar')
    .addToUi();
}

function showAudioSidebar() {
  const htmlOutput = HtmlService.createHtmlOutput(getSidebarHtml())
    .setTitle('🔊 Oxford 3000 Audio')
    .setWidth(350);
  SpreadsheetApp.getUi().showSidebar(htmlOutput);
}

function getActiveRowData() {
  try {
    const sheet = SpreadsheetApp.getActiveSheet();
    const range = sheet.getActiveRange();
    if (!range) return null;
    const row = range.getRow();
    if (row <= 1) return null; // Baris header
    
    // Ambil kolom A sampai M (13 kolom)
    const values = sheet.getRange(row, 1, 1, 13).getValues()[0];
    const formulas = sheet.getRange(row, 1, 1, 13).getFormulas()[0];
    
    function extractUrl(formula, val) {
      if (formula && typeof formula === 'string') {
        const m = formula.match(/HYPERLINK\("([^"]+)"/i);
        if (m) return m[1];
      }
      if (val && typeof val === 'string' && val.startsWith('http')) {
        return val;
      }
      return '';
    }
    
    // Kolom F & G: Internal Google Drive Audio
    const driveUk = extractUrl(formulas[5], values[5]);
    const driveUs = extractUrl(formulas[6], values[6]);
    
    // Kolom L & M: Fallback Oxford CDN Audio
    const oxfordUk = extractUrl(formulas[11], values[11]);
    const oxfordUs = extractUrl(formulas[12], values[12]);
    
    return {
      row: row,
      sheetName: sheet.getName(),
      no: values[0] || '',
      level: values[1] || '',
      word: values[2] || '',
      ipaUk: values[3] || '-',
      ipaUs: values[4] || '-',
      audioDriveUk: driveUk,
      audioDriveUs: driveUs,
      audioOxfordUk: oxfordUk,
      audioOxfordUs: oxfordUs,
      pos: values[7] || '',
      arti: values[8] || '',
      contoh: values[9] || ''
    };
  } catch (err) {
    return { error: err.toString() };
  }
}

function getSidebarHtml() {
  return `<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    body {
      background: #090d16;
      color: #f1f5f9;
      padding: 14px;
      font-size: 13px;
      line-height: 1.5;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      margin-bottom: 14px;
    }
    .title {
      font-size: 14px;
      font-weight: 800;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .status-badge {
      font-size: 10px;
      padding: 2px 7px;
      border-radius: 12px;
      font-weight: 700;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .status-badge.fallback {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border-color: rgba(245, 158, 11, 0.3);
    }
    .pulse-dot {
      width: 6px;
      height: 6px;
      background: currentColor;
      border-radius: 50%;
    }
    .card {
      background: #131c2e;
      border-radius: 12px;
      padding: 14px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      margin-bottom: 14px;
    }
    .word-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 3px;
    }
    .word-title {
      font-size: 22px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.5px;
    }
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-A1 { background: #166534; color: #bbf7d0; }
    .badge-A2 { background: #1e40af; color: #bfdbfe; }
    .badge-B1 { background: #9a3412; color: #fed7aa; }
    .badge-B2 { background: #991b1b; color: #fecaca; }
    .pos-text {
      color: #94a3b8;
      font-size: 12px;
      font-style: italic;
      margin-bottom: 10px;
    }
    .phonetic-box {
      background: #090d16;
      border-radius: 8px;
      padding: 8px 10px;
      margin-bottom: 10px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .phonetic-item {
      display: flex;
      flex-direction: column;
    }
    .phonetic-label {
      font-size: 9px;
      text-transform: uppercase;
      font-weight: 700;
      color: #64748b;
      margin-bottom: 2px;
    }
    .phonetic-val {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #38bdf8;
      font-weight: 600;
    }
    .meaning-box {
      margin-bottom: 10px;
    }
    .meaning-label {
      font-size: 10px;
      text-transform: uppercase;
      font-weight: 700;
      color: #64748b;
      margin-bottom: 2px;
    }
    .meaning-val {
      font-size: 13px;
      font-weight: 600;
      color: #f8fafc;
      line-height: 1.4;
    }
    .example-box {
      background: rgba(56, 189, 248, 0.05);
      border-left: 3px solid #38bdf8;
      border-radius: 0 6px 6px 0;
      padding: 7px 9px;
      font-size: 12px;
      color: #cbd5e1;
      font-style: italic;
      line-height: 1.4;
    }
    .section-title {
      font-size: 10px;
      text-transform: uppercase;
      font-weight: 800;
      color: #64748b;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .actions-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }
    .btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      border: none;
      transition: all 0.15s ease;
      outline: none;
    }
    .btn:active {
      transform: scale(0.97);
    }
    .btn-uk {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
    }
    .btn-uk:hover {
      background: linear-gradient(135deg, #0ea5e9, #0284c7);
    }
    .btn-us {
      background: linear-gradient(135deg, #ea580c, #c2410c);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25);
    }
    .btn-us:hover {
      background: linear-gradient(135deg, #f97316, #ea580c);
    }
    .fallback-card {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      padding: 10px;
      border: 1px dashed rgba(255, 255, 255, 0.12);
      margin-bottom: 12px;
    }
    .fallback-buttons {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }
    .btn-fallback {
      background: #1e293b;
      color: #94a3b8;
      border: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 11px;
      padding: 6px 8px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      transition: all 0.15s ease;
    }
    .btn-fallback:hover {
      background: #334155;
      color: #f1f5f9;
      border-color: #38bdf8;
    }
    .controls-panel {
      background: #131c2e;
      border-radius: 10px;
      padding: 10px 12px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      margin-bottom: 12px;
    }
    .control-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .control-row:last-child {
      margin-bottom: 0;
    }
    .control-label {
      font-size: 11px;
      color: #94a3b8;
      font-weight: 500;
    }
    .speed-pills {
      display: flex;
      gap: 4px;
    }
    .speed-btn {
      padding: 3px 7px;
      border-radius: 5px;
      background: #090d16;
      color: #94a3b8;
      font-size: 11px;
      font-weight: 600;
      border: 1px solid rgba(255, 255, 255, 0.1);
      cursor: pointer;
    }
    .speed-btn.active {
      background: #38bdf8;
      color: #090d16;
      border-color: #38bdf8;
    }
    .switch-container {
      position: relative;
      display: inline-block;
      width: 32px;
      height: 18px;
    }
    .switch-container input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #334155;
      transition: .2s;
      border-radius: 18px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 12px;
      width: 12px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .2s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #10b981;
    }
    input:checked + .slider:before {
      transform: translateX(14px);
    }
    .status-bar {
      font-size: 11px;
      color: #64748b;
      text-align: center;
      padding: 4px;
      font-style: italic;
    }
  </style>
</head>
<body>

  <div class="header">
    <div class="title">
      <span>🔊</span> Oxford Audio
    </div>
    <div id="sourceBadge" class="status-badge">
      <span class="pulse-dot"></span> <span id="badgeText">Drive Internal</span>
    </div>
  </div>

  <div id="contentArea">
    <div class="card" id="wordCard">
      <div class="word-row">
        <span class="word-title" id="wordTitle">Klik Baris Kata</span>
        <span class="badge badge-A1" id="levelBadge">CEFR</span>
      </div>
      <div class="pos-text" id="posText">Pilih salah satu baris di sheet untuk mendengar suara</div>

      <div class="phonetic-box">
        <div class="phonetic-item">
          <span class="phonetic-label">🇬🇧 UK (British)</span>
          <span class="phonetic-val" id="ipaUk">-</span>
        </div>
        <div class="phonetic-item">
          <span class="phonetic-label">🇺🇸 US (American)</span>
          <span class="phonetic-val" id="ipaUs">-</span>
        </div>
      </div>

      <div class="meaning-box">
        <div class="meaning-label">Arti (Bahasa Indonesia)</div>
        <div class="meaning-val" id="artiVal">-</div>
      </div>

      <div class="example-box" id="exampleBox">
        "Klik baris kata mana saja, audio akan langsung terdengar."
      </div>
    </div>

    <!-- MAIN BUTTONS: GOOGLE DRIVE INTERNAL -->
    <div class="section-title">
      📁 Audio Internal (Google Drive)
    </div>
    <div class="actions-grid">
      <button class="btn btn-uk" id="btnDriveUk" onclick="playAudio('drive_uk')">
        <span>▶</span> 🇬🇧 UK Audio
      </button>
      <button class="btn btn-us" id="btnDriveUs" onclick="playAudio('drive_us')">
        <span>▶</span> 🇺🇸 US Audio
      </button>
    </div>

    <!-- FALLBACK BUTTONS: OXFORD LEARNERS DICTIONARIES -->
    <div class="fallback-card">
      <div class="section-title" style="color: #94a3b8; margin-bottom: 6px;">
        🌐 Cadangan: Oxford Online (Tanpa Buka Tab)
      </div>
      <div class="fallback-buttons">
        <button class="btn-fallback" onclick="playAudio('oxford_uk')">
          <span>🔊</span> Oxford UK
        </button>
        <button class="btn-fallback" onclick="playAudio('oxford_us')">
          <span>🔊</span> Oxford US
        </button>
      </div>
    </div>

    <div class="controls-panel">
      <div class="control-row">
        <span class="control-label">Putar Otomatis saat Klik Baris</span>
        <label class="switch-container">
          <input type="checkbox" id="autoPlayToggle" checked>
          <span class="slider"></span>
        </label>
      </div>
      <div class="control-row">
        <span class="control-label">Kecepatan Suara</span>
        <div class="speed-pills">
          <button class="speed-btn" onclick="setSpeed(0.8, this)">0.8x</button>
          <button class="speed-btn active" onclick="setSpeed(1.0, this)">1.0x</button>
          <button class="speed-btn" onclick="setSpeed(1.2, this)">1.2x</button>
        </div>
      </div>
    </div>
  </div>

  <div class="status-bar" id="statusBar">
    Siap memperdengarkan audio Oxford
  </div>

  <!-- Hidden HTML5 Audio Element -->
  <audio id="audioPlayer" preload="auto"></audio>

  <script>
    let currentData = null;
    let playbackSpeed = 1.0;
    let lastRow = null;
    let isPolling = true;

    const audioPlayer = document.getElementById('audioPlayer');

    function setSpeed(speed, btn) {
      playbackSpeed = speed;
      audioPlayer.playbackRate = speed;
      document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }

    function playAudio(type) {
      if (!currentData) return;
      
      let targetUrl = '';
      let isFallback = false;
      let label = '';
      
      if (type === 'drive_uk') {
        targetUrl = currentData.audioDriveUk || currentData.audioOxfordUk;
        isFallback = !currentData.audioDriveUk;
        label = 'UK (Drive Internal)';
      } else if (type === 'drive_us') {
        targetUrl = currentData.audioDriveUs || currentData.audioOxfordUs;
        isFallback = !currentData.audioDriveUs;
        label = 'US (Drive Internal)';
      } else if (type === 'oxford_uk') {
        targetUrl = currentData.audioOxfordUk;
        isFallback = true;
        label = 'UK (Oxford Fallback)';
      } else if (type === 'oxford_us') {
        targetUrl = currentData.audioOxfordUs;
        isFallback = true;
        label = 'US (Oxford Fallback)';
      }

      if (!targetUrl) {
        document.getElementById('statusBar').textContent = 'Audio tidak tersedia.';
        return;
      }

      const badge = document.getElementById('sourceBadge');
      const badgeText = document.getElementById('badgeText');
      if (isFallback) {
        badge.className = 'status-badge fallback';
        badgeText.textContent = 'Oxford CDN';
      } else {
        badge.className = 'status-badge';
        badgeText.textContent = 'Drive Internal';
      }

      document.getElementById('statusBar').textContent = 'Memutar ' + currentData.word + ' [' + label + ']...';

      audioPlayer.src = targetUrl;
      audioPlayer.playbackRate = playbackSpeed;
      
      // Auto-fallback jika Google Drive audio gagal/error
      audioPlayer.onerror = function() {
        console.warn('Audio drive error, beralih ke Oxford CDN fallback...');
        if (!isFallback) {
          const fallbackUrl = (type.includes('uk')) ? currentData.audioOxfordUk : currentData.audioOxfordUs;
          if (fallbackUrl) {
            document.getElementById('statusBar').textContent = 'Beralih ke Oxford CDN (Fallback)...';
            badge.className = 'status-badge fallback';
            badgeText.textContent = 'Oxford CDN';
            audioPlayer.src = fallbackUrl;
            audioPlayer.playbackRate = playbackSpeed;
            audioPlayer.play().catch(e => console.error(e));
          }
        }
      };

      audioPlayer.play().catch(err => {
        console.warn('Playback error, trying fallback:', err);
        // Fallback langsung ke Oxford CDN jika error play
        if (!isFallback) {
          const fallbackUrl = (type.includes('uk')) ? currentData.audioOxfordUk : currentData.audioOxfordUs;
          if (fallbackUrl) {
            audioPlayer.src = fallbackUrl;
            audioPlayer.playbackRate = playbackSpeed;
            audioPlayer.play().catch(e => console.error(e));
          }
        }
      });
    }

    function updateCard(data) {
      if (!data || !data.word) return;
      currentData = data;
      
      document.getElementById('wordTitle').textContent = data.word;
      
      const badge = document.getElementById('levelBadge');
      badge.textContent = data.level || 'CEFR';
      badge.className = 'badge badge-' + (data.level || 'A1');
      
      document.getElementById('posText').textContent = data.pos || '';
      document.getElementById('ipaUk').textContent = data.ipaUk || '-';
      document.getElementById('ipaUs').textContent = data.ipaUs || '-';
      document.getElementById('artiVal').textContent = data.arti || '-';
      document.getElementById('exampleBox').textContent = data.contoh ? ('"' + data.contoh + '"') : '-';
      
      document.getElementById('statusBar').textContent = 'Baris ' + data.row + ': ' + data.word + ' (' + data.level + ')';
    }

    function checkActiveRow() {
      if (!isPolling) return;
      google.script.run
        .withSuccessHandler(function(data) {
          if (data && data.word && data.row !== lastRow) {
            lastRow = data.row;
            updateCard(data);
            const autoPlay = document.getElementById('autoPlayToggle').checked;
            if (autoPlay) {
              playAudio('drive_uk');
            }
          }
          setTimeout(checkActiveRow, 1000);
        })
        .withFailureHandler(function(err) {
          setTimeout(checkActiveRow, 2000);
        })
        .getActiveRowData();
    }

    window.onload = function() {
      checkActiveRow();
    };
  </script>
</body>
</html>`;
}
