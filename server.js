/**
 * GLB Texture Editor - Server
 * Provides REST API for saving/loading sessions to glb-save.json
 * Usage: node server.js [port=3000]
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = parseInt(process.argv[2]) || 3000;
const SAVE_FILE = path.join(__dirname, 'glb-save.json');
const EDITOR_FILE = path.join(__dirname, 'editor.html');
const MODEL_DIR = path.join(__dirname, 'model');

// ─────────────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────────────

function loadSessions() {
  try {
    if (!fs.existsSync(SAVE_FILE)) return { sessions: [], textures: [] };
    const data = fs.readFileSync(SAVE_FILE, 'utf-8');
    const parsed = JSON.parse(data);
    if (!Array.isArray(parsed.sessions)) parsed.sessions = [];
    if (!Array.isArray(parsed.textures)) parsed.textures = Array.isArray(parsed.texture) ? parsed.texture : [];
    return parsed;
  } catch (err) {
    console.warn('Failed to load glb-save.json:', err.message);
    return { sessions: [], textures: [] };
  }
}

function makeTextureId() {
  return `tex_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function normalizeAndPoolTextures(store, accessories) {
  if (!Array.isArray(store.textures)) store.textures = [];
  const pooledTextures = store.textures;

  const byId = new Map();
  const byBase64 = new Map();
  pooledTextures.forEach(tex => {
    if (!tex || !tex.id) return;
    byId.set(tex.id, tex);
    if (typeof tex.base64 === 'string' && tex.base64.length) {
      byBase64.set(tex.base64, tex);
    }
  });

  const normalizedAccessories = (accessories || []).map(acc => {
    const nextAcc = { ...acc };
    const texList = Array.isArray(acc?.textures) ? acc.textures : [];

    nextAcc.textures = texList.map(tex => {
      const out = { ...tex };
      let textureId = out.textureId || null;

      if (typeof out.base64 === 'string' && out.base64.length) {
        const existing = byBase64.get(out.base64);
        if (existing) {
          textureId = existing.id;
        } else {
          textureId = textureId || makeTextureId();
          const pooled = {
            id: textureId,
            key: out.key || null,
            label: out.label || out.key || 'Texture',
            width: out.width || 0,
            height: out.height || 0,
            materialColor: out.materialColor || '#ffffff',
            repeatX: Number(out.repeatX) || 1,
            repeatY: Number(out.repeatY) || 1,
            base64: out.base64,
            createdAt: Date.now(),
          };
          pooledTextures.push(pooled);
          byId.set(textureId, pooled);
          byBase64.set(out.base64, pooled);
        }
      }

      delete out.base64;
      if (textureId) out.textureId = textureId;
      return out;
    });

    return nextAcc;
  });

  return normalizedAccessories;
}

function saveSessions(data) {
  try {
    data.texture = Array.isArray(data.textures) ? data.textures : [];
    fs.writeFileSync(SAVE_FILE, JSON.stringify(data, null, 2), 'utf-8');
    console.log(`✓ Sessions saved to ${SAVE_FILE}`);
  } catch (err) {
    console.error('Failed to save glb-save.json:', err.message);
    throw err;
  }
}

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(data));
}

function sendFile(res, filePath, contentType = 'text/html') {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

// ─────────────────────────────────────────────────────────────────────
// HTTP Server
// ─────────────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  // Enable CORS for API calls
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }

  // ───── Serve HTML Editor ─────
  if (pathname === '/' || pathname === '/editor') {
    sendFile(res, EDITOR_FILE, 'text/html');
    return;
  }

  // ───── API: List all sessions ─────
  if (pathname === '/api/sessions' && req.method === 'GET') {
    const data = loadSessions();
    sendJSON(res, 200, {
      success: true,
      sessions: data.sessions.map((s, idx) => ({
        id: idx,
        name: s.name,
        savedAt: s.savedAt,
        mainGlbName: s.mainGlb?.name || 'unknown',
        accessoryCount: (s.accessories || []).length,
      })),
      textureCount: (data.textures || []).length,
    });
    return;
  }

  // ───── API: List global textures ─────
  if (pathname === '/api/textures' && req.method === 'GET') {
    const data = loadSessions();
    sendJSON(res, 200, {
      success: true,
      textures: data.textures || [],
    });
    return;
  }

  // ───── API: Add texture into global library ─────
  if (pathname === '/api/texture/add' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body || '{}');
        const base64 = typeof payload.base64 === 'string' ? payload.base64 : '';
        if (!base64) {
          sendJSON(res, 400, { success: false, error: 'Texture base64 is required' });
          return;
        }

        const data = loadSessions();
        if (!Array.isArray(data.textures)) data.textures = [];

        let texture = data.textures.find(t => t?.base64 === base64);
        if (!texture) {
          texture = {
            id: makeTextureId(),
            key: payload.key || null,
            label: payload.label || payload.key || 'Texture',
            width: Number(payload.width) || 0,
            height: Number(payload.height) || 0,
            materialColor: payload.materialColor || '#ffffff',
            repeatX: Number(payload.repeatX) || 1,
            repeatY: Number(payload.repeatY) || 1,
            base64,
            createdAt: Date.now(),
          };
          data.textures.push(texture);
          saveSessions(data);
        }

        sendJSON(res, 200, {
          success: true,
          texture,
          textures: data.textures,
        });
      } catch (err) {
        sendJSON(res, 400, { success: false, error: err.message });
      }
    });
    return;
  }

  // ───── API: Update one texture in global library ─────
  if (pathname === '/api/texture/update' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body || '{}');
        const id = payload.id;
        if (!id) {
          sendJSON(res, 400, { success: false, error: 'Texture id is required' });
          return;
        }

        const data = loadSessions();
        if (!Array.isArray(data.textures)) data.textures = [];
        const tex = data.textures.find(t => t?.id === id);
        if (!tex) {
          sendJSON(res, 404, { success: false, error: 'Texture not found' });
          return;
        }

        if (payload.materialColor !== undefined) tex.materialColor = payload.materialColor || '#ffffff';
        if (payload.repeatX !== undefined) tex.repeatX = Math.max(0.1, Number(payload.repeatX) || 1);
        if (payload.repeatY !== undefined) tex.repeatY = Math.max(0.1, Number(payload.repeatY) || 1);
        if (payload.label !== undefined) tex.label = payload.label || tex.label;
        if (payload.key !== undefined) tex.key = payload.key || tex.key;

        saveSessions(data);
        sendJSON(res, 200, { success: true, texture: tex, textures: data.textures });
      } catch (err) {
        sendJSON(res, 400, { success: false, error: err.message });
      }
    });
    return;
  }

  // ───── API: Delete one texture from global library ─────
  if (pathname === '/api/texture/delete' && req.method === 'DELETE') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = body ? JSON.parse(body) : {};
        const id = payload.id || query.id;
        if (!id) {
          sendJSON(res, 400, { success: false, error: 'Texture id is required' });
          return;
        }

        const data = loadSessions();
        if (!Array.isArray(data.textures)) data.textures = [];
        const idx = data.textures.findIndex(t => t?.id === id);
        if (idx === -1) {
          sendJSON(res, 404, { success: false, error: 'Texture not found' });
          return;
        }

        data.textures.splice(idx, 1);
        saveSessions(data);
        sendJSON(res, 200, { success: true, textures: data.textures });
      } catch (err) {
        sendJSON(res, 400, { success: false, error: err.message });
      }
    });
    return;
  }

  // ───── API: Save session (new or overwrite) ─────
  if (pathname === '/api/session/save' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const { name, mainGlb, accessories, mode } = payload;
        // mode: 'new' or 'overwrite'
        // if overwrite, payload.overwriteId should be set

        if (!name) {
          sendJSON(res, 400, { success: false, error: 'Session name required' });
          return;
        }

        const data = loadSessions();
        if (!Array.isArray(data.textures)) data.textures = [];
        const normalizedAccessories = normalizeAndPoolTextures(data, accessories || []);
        const newSession = {
          name,
          savedAt: Date.now(),
          mainGlb,
          accessories: normalizedAccessories,
        };

        if (mode === 'overwrite' && payload.overwriteId !== undefined) {
          const idx = parseInt(payload.overwriteId);
          if (idx >= 0 && idx < data.sessions.length) {
            data.sessions[idx] = newSession;
            saveSessions(data);
            sendJSON(res, 200, {
              success: true,
              message: `Session "${name}" overwritten`,
              sessionId: idx,
              textures: data.textures,
            });
            return;
          }
        }

        // Default: new session
        data.sessions.push(newSession);
        saveSessions(data);
        sendJSON(res, 200, {
          success: true,
          message: `Session "${name}" saved`,
          sessionId: data.sessions.length - 1,
          textures: data.textures,
        });
      } catch (err) {
        console.error('Save session error:', err);
        sendJSON(res, 400, { success: false, error: err.message });
      }
    });
    return;
  }

  // ───── API: Load session ─────
  if (pathname === '/api/session/load' && req.method === 'GET') {
    const sessionId = parseInt(query.id);
    const data = loadSessions();
    if (sessionId < 0 || sessionId >= data.sessions.length) {
      sendJSON(res, 404, { success: false, error: 'Session not found' });
      return;
    }
    sendJSON(res, 200, {
      success: true,
      session: data.sessions[sessionId],
      textures: data.textures || [],
    });
    return;
  }

  // ───── API: Delete session ─────
  if (pathname === '/api/session/delete' && req.method === 'DELETE') {
    const sessionId = parseInt(query.id);
    const data = loadSessions();
    if (sessionId < 0 || sessionId >= data.sessions.length) {
      sendJSON(res, 404, { success: false, error: 'Session not found' });
      return;
    }
    const name = data.sessions[sessionId].name;
    data.sessions.splice(sessionId, 1);
    saveSessions(data);
    sendJSON(res, 200, { success: true, message: `Session "${name}" deleted` });
    return;
  }

  // ───── API: Get glb-save.json for manual editing ─────
  if (pathname === '/api/raw-save' && req.method === 'GET') {
    const data = loadSessions();
    sendJSON(res, 200, data);
    return;
  }

  // ───── API: List GLB files in /model folder ─────
  if (pathname === '/api/glb-list' && req.method === 'GET') {
    try {
      if (!fs.existsSync(MODEL_DIR)) {
        sendJSON(res, 200, { success: true, files: [] });
        return;
      }
      const files = fs.readdirSync(MODEL_DIR)
        .filter(f => f.toLowerCase().endsWith('.glb'))
        .map(f => ({ name: f, path: `model/${f}` }));
      sendJSON(res, 200, { success: true, files });
    } catch (err) {
      sendJSON(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // ───── API: Upload a GLB into /model folder ─────
  if (pathname === '/api/upload-glb' && req.method === 'POST') {
    // Expects multipart/form-data with a single 'file' field (GLB binary)
    // We use a simple streaming approach: read raw body and extract GLB bytes
    // Content-Type: multipart/form-data; boundary=----XYZ
    const contentType = req.headers['content-type'] || '';
    const boundaryMatch = contentType.match(/boundary=(.+)$/);
    if (!boundaryMatch) {
      sendJSON(res, 400, { success: false, error: 'Missing multipart boundary' });
      return;
    }
    const boundary = Buffer.from('--' + boundaryMatch[1].trim());

    let chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
      try {
        const body = Buffer.concat(chunks);

        // Parse multipart: find filename and binary content
        const headerEnd = Buffer.from('\r\n\r\n');
        let pos = 0;
        let fileName = null;
        let fileBuffer = null;

        while (pos < body.length) {
          // Find next boundary
          const boundaryPos = body.indexOf(boundary, pos);
          if (boundaryPos === -1) break;
          pos = boundaryPos + boundary.length + 2; // skip \r\n

          // Check for end boundary (--)
          if (body[pos - 2] === 45 && body[pos - 1] === 45) break; // '--'

          // Find header/content separator
          const hdrEnd = body.indexOf(headerEnd, pos);
          if (hdrEnd === -1) break;

          const headerStr = body.slice(pos, hdrEnd).toString();
          const nameMatch = headerStr.match(/name="([^"]+)"/);
          const fileNameMatch = headerStr.match(/filename="([^"]+)"/);

          if (nameMatch?.[1] === 'file' && fileNameMatch) {
            fileName = path.basename(fileNameMatch[1]); // strip any path
            const contentStart = hdrEnd + 4; // skip \r\n\r\n
            // Find next boundary to get content end
            const nextBoundary = body.indexOf(boundary, contentStart);
            const contentEnd = nextBoundary === -1 ? body.length : nextBoundary - 2; // strip \r\n before boundary
            fileBuffer = body.slice(contentStart, contentEnd);
            break;
          }
          pos = hdrEnd + 4;
        }

        if (!fileName || !fileBuffer) {
          sendJSON(res, 400, { success: false, error: 'Could not parse file from multipart body' });
          return;
        }

        // Only allow .glb
        if (!fileName.toLowerCase().endsWith('.glb')) {
          sendJSON(res, 400, { success: false, error: 'Only .glb files are allowed' });
          return;
        }

        // Ensure model/ dir exists
        if (!fs.existsSync(MODEL_DIR)) fs.mkdirSync(MODEL_DIR, { recursive: true });

        const destPath = path.join(MODEL_DIR, fileName);
        fs.writeFileSync(destPath, fileBuffer);
        console.log(`✓ Uploaded ${fileName} (${fileBuffer.length} bytes) → ${destPath}`);
        sendJSON(res, 200, { success: true, name: fileName, path: `model/${fileName}` });
      } catch (err) {
        console.error('Upload error:', err);
        sendJSON(res, 500, { success: false, error: err.message });
      }
    });
    return;
  }

  // ───── Serve GLB files from /model folder ─────
  if (pathname.startsWith('/model/') && req.method === 'GET') {
    const fileName = path.basename(pathname); // prevent path traversal
    const filePath = path.join(MODEL_DIR, fileName);
    if (!filePath.startsWith(MODEL_DIR)) {
      res.writeHead(403); res.end('Forbidden'); return;
    }
    sendFile(res, filePath, 'model/gltf-binary');
    return;
  }

  // ───── Static files ─────
  const staticPath = path.join(__dirname, pathname);
  if (fs.existsSync(staticPath) && fs.statSync(staticPath).isFile()) {
    const ext = path.extname(staticPath);
    const contentTypes = {
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.css': 'text/css',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.html': 'text/html',
    };
    sendFile(res, staticPath, contentTypes[ext] || 'application/octet-stream');
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('404 Not Found');
});

server.listen(PORT, () => {
  const modelExists = fs.existsSync(MODEL_DIR);
  const modelCount = modelExists ? fs.readdirSync(MODEL_DIR).filter(f => f.toLowerCase().endsWith('.glb')).length : 0;
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  GLB Texture Editor Server                                 ║
╠════════════════════════════════════════════════════════════╣
║  🌐 http://localhost:${PORT}
║  📁 Save file: ${SAVE_FILE}
║  🗂️  Model folder: ${MODEL_DIR}
║     ${modelExists ? `${modelCount} GLB file(s) found` : '⚠️  model/ folder not found — create it!'}
║                                                            ║
║  API Endpoints:                                            ║
║  • GET  /api/sessions          - List all sessions        ║
║  • POST /api/session/save      - Save/overwrite session   ║
║  • GET  /api/session/load?id=0 - Load session by ID       ║
║  • DEL  /api/session/delete?id=0 - Delete session         ║
║  • GET  /api/glb-list          - List model/ GLB files    ║
║  • POST /api/upload-glb        - Upload GLB to model/     ║
║  • GET  /model/:file.glb       - Serve GLB by path        ║
║                                                            ║
║  Put your GLB files in the model/ folder.                  ║
║  Sessions now save paths only — no more huge JSON!         ║
╚════════════════════════════════════════════════════════════╝
  `);
});

process.on('SIGINT', () => {
  console.log('\n✓ Server shutdown');
  process.exit(0);
});