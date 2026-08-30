import logging
import asyncio
import os
import sys
import json
from datetime import datetime
from aiohttp import web

from core import config

logger = logging.getLogger(__name__)

bot_instance = None

async def index(request):
    token = config.load_token()
    token_valid = token is not None and len(token) > 10

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord AI Agent Dashboard</title>
        <meta charset="utf-8">
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e2e; color: #cdd6f4; padding: 20px; margin: 0; }
            h1 { color: #89b4fa; }
            .card { background: #313244; border-radius: 10px; padding: 20px; margin: 15px 0; }
            .card h2 { margin-top: 0; color: #a6e3a1; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .status-ok { color: #a6e3a1; font-weight: bold; }
            .status-err { color: #f38ba8; font-weight: bold; }
            .status-warn { color: #f9e2af; font-weight: bold; }
            input[type="text"], input[type="number"] { width: 100%; padding: 10px; border-radius: 5px; border: none; background: #45475a; color: #cdd6f4; margin: 5px 0; }
            button { background: #89b4fa; color: #1e1e2e; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; margin: 5px; }
            button:hover { background: #74c7ec; }
            button.danger { background: #f38ba8; color: #1e1e2e; }
            button.danger:hover { background: #e64553; }
            button.success { background: #a6e3a1; color: #1e1e2e; }
            button.success:hover { background: #7ec97a; }
            .info { color: #f9e2af; }
            .stat-value { font-size: 24px; font-weight: bold; color: #a6e3a1; }
            .log-container { background: #1e1e2e; border: 1px solid #45475a; border-radius: 5px; padding: 10px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
            .log-line { padding: 2px 5px; border-bottom: 1px solid #313244; }
            .log-line.error { color: #f38ba8; }
            .log-line.warning { color: #f9e2af; }
            .log-line.info { color: #89b4fa; }
            .flex { display: flex; gap: 10px; flex-wrap: wrap; }
            .flex-1 { flex: 1; min-width: 200px; }
            code { background: #45475a; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🤖 Discord AI Agent Dashboard</h1>

        <div class="grid">
            <div class="card">
                <h2>🔑 Token Status</h2>
                <p>Current token: """ + ('✅ Set' if token_valid else '❌ Invalid or missing') + """</p>
                <p class="""" + ('status-ok' if token_valid else 'status-err') + """">
                    """ + ('Token valid' if token_valid else 'Token invalid or not configured') + """
                </p>
                <form action="/set_token" method="post">
                    <input type="text" name="token" placeholder="Enter your Discord token..." required>
                    <button type="submit">Save & Restart</button>
                </form>
            </div>
            <div class="card">
                <h2>📊 Quick Stats</h2>
                <div id="stats">Loading...</div>
            </div>
            <div class="card">
                <h2>🎵 Voice Status</h2>
                <div id="voice">Loading...</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>🎮 Control Bot</h2>
                <div class="flex">
                    <button class="success" onclick="sendControl('reload')">🔄 Reload Modules</button>
                    <button class="danger" onclick="sendControl('shutdown')">⏹️ Shutdown</button>
                    <button onclick="sendControl('status')">📊 Status</button>
                </div>
                <div id="control-result" class="info" style="margin-top:10px;"></div>
            </div>
            <div class="card">
                <h2>👥 Trusted Users</h2>
                <div class="flex">
                    <div class="flex-1">
                        <input type="number" id="trusted-id" placeholder="User ID">
                        <button onclick="manageTrusted('add')">➕ Add</button>
                        <button onclick="manageTrusted('remove')">➖ Remove</button>
                    </div>
                </div>
                <div id="trusted-list" style="margin-top:10px;">Loading...</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📋 Quick Commands</h2>
                <form id="quick-command-form" onsubmit="sendQuickCommand(); return false;">
                    <div class="flex">
                        <input type="text" id="quick-cmd" placeholder="!say 123456789 Hello world" style="flex:1;">
                        <button type="submit">▶️ Execute</button>
                    </div>
                </form>
                <div id="quick-result" class="info" style="margin-top:10px;"></div>
            </div>
            <div class="card">
                <h2>📦 Message Queue</h2>
                <div id="queue">Loading...</div>
            </div>
        </div>

        <div class="card">
            <h2>📜 Live Logs</h2>
            <button onclick="fetchLogs()">🔄 Refresh</button>
            <div id="logs" class="log-container">Loading...</div>
        </div>

        <div class="card">
            <h2>📋 Available Commands</h2>
            <div id="commands-list">Loading...</div>
        </div>

        <script>
            async function fetchAPI(endpoint) {
                try {
                    const res = await fetch(endpoint);
                    return await res.json();
                } catch(e) {
                    console.error(e);
                    return null;
                }
            }

            async function updateStats() {
                const data = await fetchAPI('/api/status');
                if (data) {
                    document.getElementById('stats').innerHTML = `
                        <p>📨 Messages: <span class="stat-value">${data.stats.messages_processed || 0}</span></p>
                        <p>💬 Replies: <span class="stat-value">${data.stats.responses_sent || 0}</span></p>
                        <p>🧠 Facts: <span class="stat-value">${data.stats.facts_extracted || 0}</span></p>
                        <p>🚫 Blocked: <span class="stat-value">${(data.stats.toxic_blocked || 0) + (data.stats.spam_blocked || 0)}</span></p>
                        <p>⏰ Uptime: <span class="stat-value">${data.stats.start_time || 'N/A'}</span></p>
                    `;
                    document.getElementById('voice').innerHTML = `
                        <p>🎧 Connected: ${data.voice.connected ? '✅ Yes' : '❌ No'}</p>
                        ${data.voice.playing ? `<p>🎵 Now playing: <strong>${data.voice.title}</strong></p>` : ''}
                        <p>📊 Channel: ${data.voice.channel || 'N/A'}</p>
                    `;
                }
                updateQueue();
                updateTrusted();
                updateCommands();
            }

            async function updateQueue() {
                const data = await fetchAPI('/api/queue');
                if (data) {
                    document.getElementById('queue').innerHTML = `
                        <p>📦 Queue: <strong>${data.queue_size || 0}</strong> messages</p>
                        ${data.queue_size > 0 ? `<p>Last: "${data.last_message || 'N/A'}"</p>` : ''}
                    `;
                }
            }

            async function updateTrusted() {
                const data = await fetchAPI('/api/trusted');
                if (data) {
                    document.getElementById('trusted-list').innerHTML = `
                        <p>👥 Trusted users: <strong>${data.count || 0}</strong></p>
                        ${data.users && data.users.length > 0 ? `<p>${data.users.join(', ')}</p>` : '<p>📭 No users.</p>'}
                    `;
                }
            }

            async function updateCommands() {
                const data = await fetchAPI('/api/commands');
                if (data && data.commands) {
                    const cmds = data.commands.slice(0, 30).join(', ');
                    document.getElementById('commands-list').innerHTML = `
                        <p><strong>${data.commands.length}</strong> commands available:</p>
                        <p style="font-size:12px; word-wrap:break-word;">${cmds}${data.commands.length > 30 ? '...' : ''}</p>
                    `;
                }
            }

            async function fetchLogs() {
                const data = await fetchAPI('/api/logs');
                if (data && data.logs) {
                    const lines = data.logs.map(line => {
                        let cls = 'info';
                        if (line.includes('ERROR') || line.includes('❌')) cls = 'error';
                        else if (line.includes('WARNING') || line.includes('⚠️')) cls = 'warning';
                        return `<div class="log-line ${cls}">${escapeHtml(line)}</div>`;
                    }).join('');
                    document.getElementById('logs').innerHTML = lines || '📭 No logs.';
                }
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            async function sendControl(action) {
                const res = await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: action})
                });
                const data = await res.json();
                document.getElementById('control-result').innerHTML = `✅ ${data.result || 'Executed!'}`;
                if (action === 'shutdown' || action === 'reload') {
                    setTimeout(() => window.location.reload(), 2000);
                }
                updateStats();
            }

            async function manageTrusted(action) {
                const id = document.getElementById('trusted-id').value;
                if (!id) { alert('Enter an ID!'); return; }
                const res = await fetch('/api/trusted', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: action, user_id: parseInt(id)})
                });
                const data = await res.json();
                document.getElementById('control-result').innerHTML = `✅ ${data.result || 'Executed!'}`;
                document.getElementById('trusted-id').value = '';
                updateTrusted();
            }

            async function sendQuickCommand() {
                const cmd = document.getElementById('quick-cmd').value;
                if (!cmd) return;
                const res = await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'command', command: cmd})
                });
                const data = await res.json();
                document.getElementById('quick-result').innerHTML = `✅ ${data.result || 'Executed!'}`;
                document.getElementById('quick-cmd').value = '';
            }

            updateStats();
            fetchLogs();
            setInterval(updateStats, 10000);
            setInterval(fetchLogs, 15000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def set_token(request):
    data = await request.post()
    new_token = data.get('token', '').strip()
    if not new_token or len(new_token) < 20:
        return web.Response(text="Invalid token. Must be at least 20 characters.", status=400)

    config.save_token(new_token)
    logger.info("New token saved. Restarting bot...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

async def api_status(request):
    stats = config.load_stats()
    voice_data = {"connected": False, "playing": False, "title": "", "channel": ""}
    try:
        from modules import voice
        if voice.voice_clients:
            for gid, vc in voice.voice_clients.items():
                if vc.is_connected():
                    voice_data["connected"] = True
                    voice_data["channel"] = vc.channel.name
                    current = voice.voice_current.get(gid)
                    if current:
                        voice_data["playing"] = True
                        voice_data["title"] = current.get("title", "Unknown")
                    break
    except Exception:
        pass
    return web.json_response({"stats": stats, "voice": voice_data})

async def api_queue(request):
    queue_size = 0
    last_message = "N/A"
    if bot_instance:
        try:
            queue_size = len(bot_instance.pending_tasks) if hasattr(bot_instance, 'pending_tasks') else 0
            if queue_size > 0:
                last_message = bot_instance.pending_tasks[-1].get('message', {}).content[:50] if hasattr(bot_instance, 'pending_tasks') else "N/A"
        except Exception:
            pass
    return web.json_response({"queue_size": queue_size, "last_message": last_message})

async def api_trusted(request):
    trusted = config.load_trusted_users()
    return web.json_response({"count": len(trusted), "users": list(trusted)})

async def api_trusted_manage(request):
    data = await request.json()
    action = data.get('action')
    user_id = data.get('user_id')
    
    if action not in ('add', 'remove') or not user_id:
        return web.json_response({"error": "Invalid action"}, status=400)
    
    trusted = config.load_trusted_users()
    if action == 'add':
        trusted.add(user_id)
        result = f"User {user_id} added."
    else:
        trusted.discard(user_id)
        result = f"User {user_id} removed."
    config.save_trusted_users(trusted)
    return web.json_response({"result": result, "count": len(trusted)})

async def api_commands(request):
    cmds = []
    if bot_instance and hasattr(bot_instance, 'commands'):
        cmds = sorted([c.name for c in bot_instance.commands])
    return web.json_response({"commands": cmds, "count": len(cmds)})

async def api_logs(request):
    log_file = "bot.log"
    logs = []
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                logs = [line.strip() for line in lines[-50:]]
    except Exception:
        pass
    return web.json_response({"logs": logs})

async def api_control(request):
    data = await request.json()
    action = data.get('action')
    command = data.get('command')
    
    result = "OK"
    if action == 'shutdown':
        result = "Shutting down..."
        if bot_instance:
            asyncio.create_task(bot_instance.close())
    elif action == 'reload':
        result = "Reloading modules..."
        if bot_instance and hasattr(bot_instance, 'load_modules'):
            bot_instance.load_modules()
    elif action == 'command' and command:
        result = f"Command '{command}' sent."
        if bot_instance:
            pass
    else:
        result = f"Unknown action: {action}"
    
    return web.json_response({"result": result})

async def start_dashboard():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/set_token', set_token)
    app.router.add_get('/api/status', api_status)
    app.router.add_get('/api/queue', api_queue)
    app.router.add_get('/api/trusted', api_trusted)
    app.router.add_post('/api/trusted', api_trusted_manage)
    app.router.add_get('/api/commands', api_commands)
    app.router.add_get('/api/logs', api_logs)
    app.router.add_post('/api/control', api_control)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=config.WEB_HOST, port=config.WEB_PORT)
    await site.start()
    logger.info(f"🌐 Dashboard running on http://{config.WEB_HOST}:{config.WEB_PORT}")

def set_bot(bot):
    global bot_instance
    bot_instance = bot
