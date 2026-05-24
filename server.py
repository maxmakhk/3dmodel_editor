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

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)
CORS(app)

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SCRIPT_DIR = Path(__file__).parent
SAVE_FILE = SCRIPT_DIR / 'glb-save.json'
SAVE_DIR = SCRIPT_DIR / 'save'
TEXTURES_FILE = SAVE_DIR / 'textures.json'
EDITOR_FILE = SCRIPT_DIR / 'editor.html'
MODEL_DIR = SCRIPT_DIR / 'assets' / 'items'

# ─────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────

import re

def get_safe_session_filename(name):
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower()
    return f"{safe_name}.json"

def load_sessions():
    """Load sessions from save/ directory"""
    try:
        if not SAVE_DIR.exists():
            SAVE_DIR.mkdir(parents=True, exist_ok=True)

        # Auto-rename bartender_save..json to bartender_save.json
        double_dot = SAVE_DIR / 'bartender_save..json'
        single_dot = SAVE_DIR / 'bartender_save.json'
        if double_dot.exists():
            try:
                double_dot.rename(single_dot)
                print("✓ Automatically corrected and renamed bartender_save..json to bartender_save.json", file=sys.stderr)
            except Exception as re_err:
                print(f"Warning: Failed to rename bartender_save..json: {re_err}", file=sys.stderr)

        # One-time migration of textures
        if not TEXTURES_FILE.exists() and SAVE_FILE.exists():
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                migrated_textures = old_data.get('textures', old_data.get('texture', []))
                with open(TEXTURES_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'textures': migrated_textures}, f, indent=2, ensure_ascii=False)
                print(f"✓ Successfully migrated {len(migrated_textures)} textures from glb-save.json to {TEXTURES_FILE}", file=sys.stderr)
            except Exception as mig_err:
                print(f"Warning: Failed to migrate textures: {mig_err}", file=sys.stderr)

        # Load global textures
        textures = []
        if TEXTURES_FILE.exists():
            try:
                with open(TEXTURES_FILE, 'r', encoding='utf-8') as f:
                    tex_data = json.load(f)
                textures = tex_data.get('textures', tex_data.get('texture', []))
                if not isinstance(textures, list):
                    textures = []
            except Exception as tex_err:
                print(f"Warning: Failed to load textures.json: {tex_err}", file=sys.stderr)

        # Scan save/ folder for all session files (excluding textures.json)
        sessions = []
        for file_path in SAVE_DIR.glob('*.json'):
            if file_path.name.lower() == 'textures.json':
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                
                # Ensure name exists, fallback to filename
                if not session.get('name'):
                    session['name'] = file_path.stem
                
                # Ensure savedAt exists, fallback to file mtime
                if not session.get('savedAt'):
                    session['savedAt'] = int(file_path.stat().st_mtime * 1000)
                
                session['_filename'] = file_path.name # Record filename
                sessions.append(session)
            except Exception as file_err:
                print(f"Warning: Failed to parse session file {file_path.name}: {file_err}", file=sys.stderr)

        # Sort sessions by savedAt ascending
        sessions.sort(key=lambda s: s.get('savedAt', 0))

        return {'sessions': sessions, 'textures': textures}
    except Exception as e:
        print(f"Error: Failed to load sessions: {e}", file=sys.stderr)
        return {'sessions': [], 'textures': [], '_loadError': str(e)}


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

def save_textures(textures):
    """Save global textures to save/textures.json"""
    try:
        if not SAVE_DIR.exists():
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
        with open(TEXTURES_FILE, 'w', encoding='utf-8') as f:
            json.dump({'textures': textures}, f, indent=2, ensure_ascii=False)
        print(f"✓ Textures saved to {TEXTURES_FILE}", file=sys.stderr)
    except Exception as e:
        print(f"Error: Failed to save textures: {e}", file=sys.stderr)
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
        mainGlbs = payload.get('mainGlbs', [])
        accessories = payload.get('accessories', [])
        mode = payload.get('mode', 'new')
        overwriteId = payload.get('overwriteId')
        cameraData = payload.get('cameraData')
        cameraPreset = payload.get('cameraPreset')

        if not name:
            return jsonify({'success': False, 'error': 'Session name required'}), 400

        safe_filename = get_safe_session_filename(name)
        file_path = SAVE_DIR / safe_filename

        data = load_sessions()
        normalized_accessories = normalize_and_pool_textures(data, accessories)

        new_session = {
            'name': name,
            'savedAt': int(datetime.now().timestamp() * 1000),
            'mainGlb': mainGlb,
            'mainGlbs': mainGlbs,
            'accessories': normalized_accessories,
            'cameraData': cameraData or None,
            'cameraPreset': cameraPreset or None,
        }

        existing_data = {}

        # Handle overwrite
        if mode == 'overwrite' and overwriteId is not None:
            idx = int(overwriteId)
            if 0 <= idx < len(data['sessions']):
                old_session = data['sessions'][idx]
                old_filename = old_session.get('_filename')
                
                # Delete old file if name changed
                if old_filename and old_filename != safe_filename:
                    old_file_path = SAVE_DIR / old_filename
                    if old_file_path.exists():
                        try:
                            old_file_path.unlink()
                            print(f"✓ Deleted old session file during rename: {old_filename}", file=sys.stderr)
                        except Exception as unlink_err:
                            print(f"Warning: Failed to delete old session file {old_filename}: {unlink_err}", file=sys.stderr)

                target_old_path = SAVE_DIR / old_filename if old_filename else file_path
                if target_old_path.exists():
                    try:
                        with open(target_old_path, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except Exception:
                        pass
        else:
            # New session - read existing file with same slug if it exists to merge
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    pass

        # Merge custom fields with new editor state
        merged_session = {**existing_data}
        merged_session.update({
            'name': new_session['name'],
            'savedAt': new_session['savedAt'],
            'mainGlb': new_session['mainGlb'],
            'mainGlbs': new_session['mainGlbs'],
            'accessories': new_session['accessories'],
            'cameraData': new_session['cameraData'],
            'cameraPreset': new_session['cameraPreset']
        })

        # Save individual session file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_session, f, indent=2, ensure_ascii=False)
        print(f"✓ Session \"{name}\" saved to {file_path}", file=sys.stderr)

        # Save global textures
        save_textures(data.get('textures', []))

        # Reload sessions to get stable order and final index
        updated_data = load_sessions()
        final_idx = -1
        for i, s in enumerate(updated_data['sessions']):
            if s.get('_filename') == safe_filename:
                final_idx = i
                break
        
        if final_idx == -1:
            final_idx = len(updated_data['sessions']) - 1

        return jsonify({
            'success': True,
            'message': f'Session "{name}" overwritten' if mode == 'overwrite' else f'Session "{name}" saved',
            'sessionId': final_idx,
            'textures': updated_data.get('textures', []),
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
        
        session = dict(data['sessions'][sessionId])
        # Strip _filename
        session.pop('_filename', None)
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
        if sessionId < 0 or sessionId >= len(data.get('sessions', [])):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        target_session = data['sessions'][sessionId]
        filename = target_session.get('_filename')
        name = target_session.get('name', 'Untitled')
        
        if filename:
            file_path = SAVE_DIR / filename
            if file_path.exists():
                file_path.unlink()
                print(f"✓ Deleted session file: {filename}", file=sys.stderr)
        
        return jsonify({'success': True, 'message': f'Session "{name}" deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/raw-save', methods=['GET'])
def get_raw_save():
    """Get raw glb-save.json for manual editing"""
    data = load_sessions()
    return jsonify(data)


@app.route('/api/glb-list', methods=['GET'])
def list_glb_files():
    """List GLB files in assets/items/"""
    try:
        if not MODEL_DIR.exists():
            return jsonify({'success': True, 'files': []})
        files = []
        for f in MODEL_DIR.glob('*.glb'):
            files.append({'name': f.name, 'path': f'assets/items/{f.name}'})
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload-glb', methods=['POST'])
def upload_glb():
    """Upload GLB to assets/items/"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        if not file.filename.lower().endswith('.glb'):
            return jsonify({'success': False, 'error': 'Only .glb files are allowed'}), 400
        
        if not MODEL_DIR.exists():
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            
        filename = os.path.basename(file.filename)
        dest_path = MODEL_DIR / filename
        file.save(str(dest_path))
        print(f"✓ Uploaded {filename} → {dest_path}", file=sys.stderr)
        return jsonify({'success': True, 'name': filename, 'path': f'/assets/items/{filename}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/assets/items/<path:filename>', methods=['GET'])
def serve_assets_items(filename):
    """Serve GLB files from assets/items/"""
    return send_from_directory(MODEL_DIR, filename)


@app.route('/model/<path:filename>', methods=['GET'])
def serve_legacy_model(filename):
    """Fallback serve files requested under legacy /model/ from assets/items/"""
    return send_from_directory(MODEL_DIR, filename)


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
    try:
        load_sessions()
    except Exception as e:
        print(f"Initial session loading failed: {e}", file=sys.stderr)
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  GLB Texture Editor Server (Python Flask)                  ║
╠════════════════════════════════════════════════════════════╣
║  🌐 Server running at http://localhost:{PORT}
║  📁 Save folder: {SAVE_DIR}
║  🗂️  Model folder: {MODEL_DIR}
║  ℹ️  Open browser to: http://localhost:{PORT}
║                                                            ║
║  API Endpoints:                                            ║
║  • GET  /api/sessions          - List all sessions        ║
║  • POST /api/session/save      - Save/overwrite session   ║
║  • GET  /api/session/load?id=0 - Load session by ID       ║
║  • DEL  /api/session/delete?id=0 - Delete session         ║
║  • GET  /api/glb-list          - List model/ GLB files    ║
║  • POST /api/upload-glb        - Upload GLB to model/     ║
║  • GET  /assets/items/:file.glb - Serve GLB by path        ║
║                                                            ║
║  Put your GLB files in the assets/items/ folder.           ║
║  Sessions save individually to save/ folder as JSON files! ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=PORT, debug=False)
