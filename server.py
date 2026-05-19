#!/usr/bin/env python3
"""
GLB Texture Editor - Python Server (Flask)
Provides REST API for saving/loading sessions to glb-save.json
Usage: python3 server.py [port=3000]
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SCRIPT_DIR = Path(__file__).parent
SAVE_FILE = SCRIPT_DIR / 'glb-save.json'
EDITOR_FILE = SCRIPT_DIR / 'editor.html'

# ─────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────

def load_sessions():
    """Load sessions from glb-save.json"""
    try:
        if SAVE_FILE.exists():
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as je:
                print(f"Warning: glb-save.json is corrupted (JSON parse error): {je}", file=sys.stderr)
                # Return a clean structure but note the error
                return {"sessions": [], "textures": [], "_loadError": "JSON parse error"}
            except UnicodeDecodeError as ue:
                print(f"Warning: glb-save.json has encoding issues: {ue}", file=sys.stderr)
                return {"sessions": [], "textures": [], "_loadError": "Encoding error"}
            
            # Validate and normalize data structure
            if not isinstance(data.get('sessions'), list):
                print(f"Warning: sessions field is not a list, initializing empty", file=sys.stderr)
                data['sessions'] = []
            
            if not isinstance(data.get('textures'), list):
                # Try legacy 'texture' field
                if isinstance(data.get('texture'), list):
                    data['textures'] = data.get('texture')
                else:
                    print(f"Warning: textures field is not a list, initializing empty", file=sys.stderr)
                    data['textures'] = []
            
            print(f"✓ Loaded {len(data['sessions'])} sessions and {len(data['textures'])} textures from glb-save.json", file=sys.stderr)
            return data
        else:
            print(f"Info: glb-save.json does not exist yet", file=sys.stderr)
            return {"sessions": [], "textures": []}
    except Exception as e:
        print(f"Error: Failed to load glb-save.json: {e}", file=sys.stderr)
        return {"sessions": [], "textures": [], "_loadError": str(e)}


def make_texture_id():
    return f"tex_{int(datetime.now().timestamp() * 1000):x}_{os.urandom(3).hex()}"


def normalize_and_pool_textures(store, accessories):
    if not isinstance(store.get('textures'), list):
        store['textures'] = []

    pooled = store['textures']
    by_id = {t.get('id'): t for t in pooled if isinstance(t, dict) and t.get('id')}
    by_base64 = {
        t.get('base64'): t
        for t in pooled
        if isinstance(t, dict) and isinstance(t.get('base64'), str) and t.get('base64')
    }

    normalized_accessories = []
    for acc in (accessories or []):
        next_acc = dict(acc or {})
        tex_list = next_acc.get('textures') if isinstance(next_acc.get('textures'), list) else []
        next_textures = []

        for tex in tex_list:
            out = dict(tex or {})
            texture_id = out.get('textureId')
            base64_data = out.get('base64') if isinstance(out.get('base64'), str) else None

            if base64_data:
                existing = by_base64.get(base64_data)
                if existing:
                    texture_id = existing.get('id')
                else:
                    texture_id = texture_id or make_texture_id()
                    pooled_tex = {
                        'id': texture_id,
                        'key': out.get('key'),
                        'label': out.get('label') or out.get('key') or 'Texture',
                        'width': out.get('width') or 0,
                        'height': out.get('height') or 0,
                        'materialColor': out.get('materialColor') or '#ffffff',
                        'repeatX': float(out.get('repeatX') or 1),
                        'repeatY': float(out.get('repeatY') or 1),
                        'base64': base64_data,
                        'createdAt': int(datetime.now().timestamp() * 1000),
                    }
                    pooled.append(pooled_tex)
                    by_id[texture_id] = pooled_tex
                    by_base64[base64_data] = pooled_tex

            out.pop('base64', None)
            if texture_id:
                out['textureId'] = texture_id
            next_textures.append(out)

        next_acc['textures'] = next_textures
        normalized_accessories.append(next_acc)

    return normalized_accessories

def save_sessions(data):
    """Save sessions to glb-save.json"""
    try:
        # Ensure sessions and textures are lists
        if not isinstance(data.get('sessions'), list):
            data['sessions'] = []
        if not isinstance(data.get('textures'), list):
            data['textures'] = []
        
        # Keep legacy 'texture' field in sync for backward compatibility
        data['texture'] = data.get('textures', [])
        
        # Create backup before overwriting (optional safety measure)
        backup_file = SAVE_FILE.with_suffix('.json.bak')
        if SAVE_FILE.exists():
            try:
                import shutil
                shutil.copy2(SAVE_FILE, backup_file)
                print(f"✓ Created backup: {backup_file}", file=sys.stderr)
            except Exception as be:
                print(f"Warning: Could not create backup: {be}", file=sys.stderr)
        
        # Write sessions to file
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Sessions saved to {SAVE_FILE} ({len(data['sessions'])} sessions, {len(data['textures'])} textures)", file=sys.stderr)
    except Exception as e:
        print(f"Error: Failed to save glb-save.json: {e}", file=sys.stderr)
        raise

# ─────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────

@app.route('/')
@app.route('/editor')
def serve_editor():
    """Serve the HTML editor"""
    return send_file(EDITOR_FILE, mimetype='text/html')

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions"""
    try:
        data = load_sessions()
        sessions_info = [
            {
                'id': idx,
                'name': s.get('name', 'Untitled'),
                'savedAt': s.get('savedAt', 0),
                'mainGlbName': s.get('mainGlb', {}).get('name', 'unknown'),
                'accessoryCount': len(s.get('accessories', [])),
            }
            for idx, s in enumerate(data.get('sessions', []))
        ]
        print(f"✓ Listed {len(sessions_info)} sessions", file=sys.stderr)
        return jsonify({'success': True, 'sessions': sessions_info, 'textureCount': len(data.get('textures', []))})
    except Exception as e:
        print(f"Error: List sessions failed: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e), 'sessions': []}), 500


@app.route('/api/textures', methods=['GET'])
def list_textures():
    """List global pooled textures"""
    data = load_sessions()
    return jsonify({'success': True, 'textures': data.get('textures', [])})


@app.route('/api/texture/add', methods=['POST'])
def add_texture():
    """Add one texture into global texture library"""
    try:
        payload = request.get_json() or {}
        base64_data = payload.get('base64') if isinstance(payload.get('base64'), str) else ''
        if not base64_data:
            return jsonify({'success': False, 'error': 'Texture base64 is required'}), 400

        data = load_sessions()
        textures = data.get('textures', []) if isinstance(data.get('textures'), list) else []
        data['textures'] = textures

        texture = next((t for t in textures if isinstance(t, dict) and t.get('base64') == base64_data), None)
        if texture is None:
            texture = {
                'id': make_texture_id(),
                'key': payload.get('key'),
                'label': payload.get('label') or payload.get('key') or 'Texture',
                'width': int(payload.get('width') or 0),
                'height': int(payload.get('height') or 0),
                'materialColor': payload.get('materialColor') or '#ffffff',
                'repeatX': float(payload.get('repeatX') or 1),
                'repeatY': float(payload.get('repeatY') or 1),
                'base64': base64_data,
                'createdAt': int(datetime.now().timestamp() * 1000),
            }
            textures.append(texture)
            save_sessions(data)

        return jsonify({'success': True, 'texture': texture, 'textures': textures})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/texture/update', methods=['POST'])
def update_texture():
    """Update one texture metadata in global texture library"""
    try:
        payload = request.get_json() or {}
        texture_id = payload.get('id')
        if not texture_id:
            return jsonify({'success': False, 'error': 'Texture id is required'}), 400

        data = load_sessions()
        textures = data.get('textures', []) if isinstance(data.get('textures'), list) else []
        data['textures'] = textures
        texture = next((t for t in textures if isinstance(t, dict) and t.get('id') == texture_id), None)
        if texture is None:
            return jsonify({'success': False, 'error': 'Texture not found'}), 404

        if 'materialColor' in payload:
            texture['materialColor'] = payload.get('materialColor') or '#ffffff'
        if 'repeatX' in payload:
            texture['repeatX'] = max(0.1, float(payload.get('repeatX') or 1))
        if 'repeatY' in payload:
            texture['repeatY'] = max(0.1, float(payload.get('repeatY') or 1))
        if 'label' in payload and payload.get('label'):
            texture['label'] = payload.get('label')
        if 'key' in payload and payload.get('key'):
            texture['key'] = payload.get('key')

        save_sessions(data)
        return jsonify({'success': True, 'texture': texture, 'textures': textures})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/texture/delete', methods=['DELETE'])
def delete_texture():
    """Delete one texture from global texture library"""
    try:
        payload = request.get_json(silent=True) or {}
        texture_id = payload.get('id') or request.args.get('id')
        if not texture_id:
            return jsonify({'success': False, 'error': 'Texture id is required'}), 400

        data = load_sessions()
        textures = data.get('textures', []) if isinstance(data.get('textures'), list) else []
        data['textures'] = textures
        idx = next((i for i, t in enumerate(textures) if isinstance(t, dict) and t.get('id') == texture_id), -1)
        if idx < 0:
            return jsonify({'success': False, 'error': 'Texture not found'}), 404

        textures.pop(idx)
        save_sessions(data)
        return jsonify({'success': True, 'textures': textures})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/session/save', methods=['POST'])
def save_session():
    """Save a new or overwrite existing session"""
    try:
        payload = request.get_json()
        name = payload.get('name', '').strip()
        mainGlb = payload.get('mainGlb')
        accessories = payload.get('accessories', [])
        mode = payload.get('mode', 'new')
        overwriteId = payload.get('overwriteId')

        if not name:
            return jsonify({'success': False, 'error': 'Session name required'}), 400

        data = load_sessions()
        normalized_accessories = normalize_and_pool_textures(data, accessories)

        new_session = {
            'name': name,
            'savedAt': int(datetime.now().timestamp() * 1000),
            'mainGlb': mainGlb,
            'accessories': normalized_accessories,
        }

        if mode == 'overwrite' and overwriteId is not None:
            idx = int(overwriteId)
            if 0 <= idx < len(data['sessions']):
                data['sessions'][idx] = new_session
                save_sessions(data)
                return jsonify({
                    'success': True,
                    'message': f'Session "{name}" overwritten',
                    'sessionId': idx,
                    'textures': data.get('textures', []),
                })

        # Default: new session
        data['sessions'].append(new_session)
        save_sessions(data)
        return jsonify({
            'success': True,
            'message': f'Session "{name}" saved',
            'sessionId': len(data['sessions']) - 1,
            'textures': data.get('textures', []),
        })

    except Exception as e:
        print(f"Error: Save session failed: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/session/load', methods=['GET'])
def load_session():
    """Load session by ID"""
    try:
        sessionId = int(request.args.get('id', -1))
        data = load_sessions()
        
        if sessionId < 0 or sessionId >= len(data.get('sessions', [])):
            error_msg = f'Session {sessionId} not found. Available: {len(data.get("sessions", []))}'
            print(f"Warning: {error_msg}", file=sys.stderr)
            return jsonify({'success': False, 'error': error_msg}), 404
        
        session = data['sessions'][sessionId]
        print(f"✓ Loaded session {sessionId}: {session.get('name', 'Untitled')}", file=sys.stderr)
        
        return jsonify({
            'success': True,
            'session': session,
            'textures': data.get('textures', []),
        })
    except ValueError as ve:
        return jsonify({'success': False, 'error': f'Invalid session ID: {ve}'}), 400
    except Exception as e:
        print(f"Error: Load session failed: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/session/delete', methods=['DELETE'])
def delete_session():
    """Delete session by ID"""
    try:
        sessionId = int(request.args.get('id', -1))
        data = load_sessions()
        if sessionId < 0 or sessionId >= len(data['sessions']):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        name = data['sessions'][sessionId].get('name', 'Untitled')
        data['sessions'].pop(sessionId)
        save_sessions(data)
        return jsonify({'success': True, 'message': f'Session "{name}" deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/raw-save', methods=['GET'])
def get_raw_save():
    """Get raw glb-save.json for manual editing"""
    data = load_sessions()
    return jsonify(data)

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory(SCRIPT_DIR, filename)
    except Exception:
        return 'Not Found', 404

# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  GLB Texture Editor Server (Python Flask)                  ║
╠════════════════════════════════════════════════════════════╣
║  🌐 Server running at http://localhost:{PORT}
║  📁 Save file: {SAVE_FILE}
║  ℹ️  Open browser to: http://localhost:{PORT}
║                                                            ║
║  API Endpoints:                                            ║
║  • GET  /api/sessions          - List all sessions        ║
║  • POST /api/session/save      - Save/overwrite session   ║
║  • GET  /api/session/load?id=0 - Load session by ID       ║
║  • DEL  /api/session/delete?id=0 - Delete session         ║
║  • GET  /api/raw-save          - Get raw JSON             ║
║                                                            ║
║  You can manually edit glb-save.json:                      ║
║  • JSON format: {{ "sessions": [...] }}                   ║
║  • Reload page to see changes                             ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=PORT, debug=False)
