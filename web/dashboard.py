import logging
import asyncio
import os
import sys
from aiohttp import web

from core import config

logger = logging.getLogger(__name__)

async def index(request):
    token = config.load_token()
    token_valid = token is not None and len(token) > 10

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord AI Agent Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e2e; color: #cdd6f4; padding: 20px; }}
            h1 {{ color: #89b4fa; }}
            .card {{ background: #313244; border-radius: 10px; padding: 20px; margin: 15px 0; }}
            .status-ok {{ color: #a6e3a1; font-weight: bold; }}
            .status-err {{ color: #f38ba8; font-weight: bold; }}
            input[type="text"] {{ width: 70%%; padding: 10px; border-radius: 5px; border: none; background: #45475a; color: #cdd6f4; }}
            button {{ background: #89b4fa; color: #1e1e2e; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            button:hover {{ background: #74c7ec; }}
            .info {{ color: #f9e2af; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #a6e3a1; }}
        </style>
    </head>
    <body>
        <h1>🤖 Discord AI Agent Dashboard</h1>
        <div class="grid">
            <div class="card">
                <h2>🔑 Token Status</h2>
                <p>Current token: {'✅ Set' if token_valid else '❌ Invalid or missing'}</p>
                <p class="{'status-ok' if token_valid else 'status-err'}">
                    {'Token valid' if token_valid else 'Token invalid or not configured'}
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
        </div>
        <div class="card">
            <h2>🎵 Voice Status</h2>
            <div id="voice">Loading...</div>
        </div>
        <div class="card">
            <h2>📋 Available Commands</h2>
            <p><code>!friends</code> - List friends<br>
            <code>!add_friend &lt;id&gt;</code> - Add friend<br>
            <code>!remove_friend &lt;id&gt;</code> - Remove friend<br>
            <code>!block &lt;id&gt;</code> - Block user<br>
            <code>!unblock &lt;id&gt;</code> - Unblock user<br>
            <code>!send &lt;channel_id&gt; &lt;text&gt;</code> - Send message<br>
            <code>!edit &lt;msg_id&gt; &lt;channel_id&gt; &lt;text&gt;</code> - Edit message<br>
            <code>!delete &lt;msg_id&gt; &lt;channel_id&gt;</code> - Delete message<br>
            <code>!react &lt;msg_id&gt; &lt;channel_id&gt; &lt;emoji&gt;</code> - Add reaction<br>
            <code>!pin &lt;msg_id&gt; &lt;channel_id&gt;</code> - Pin message<br>
            <code>!join</code> - Join voice<br>
            <code>!leave</code> - Leave voice<br>
            <code>!play &lt;query&gt;</code> - Play music<br>
            <code>!pause</code> - Pause<br>
            <code>!resume</code> - Resume<br>
            <code>!stop</code> - Stop<br>
            <code>!skip</code> - Skip<br>
            <code>!np</code> - Now playing<br>
            <code>!queue</code> - Show queue<br>
            <code>!volume &lt;0-100&gt;</code> - Set volume<br>
            <code>!status &lt;text&gt;</code> - Set custom status<br>
            <code>!avatar</code> - Change avatar (attach image)<br>
            <code>!username &lt;name&gt;</code> - Change username<br>
            <code>!online/idle/dnd/invisible</code> - Set status<br>
            <code>!create_channel &lt;guild_id&gt; &lt;name&gt; [text/voice/category]</code><br>
            <code>!delete_channel &lt;channel_id&gt;</code><br>
            <code>!channels &lt;guild_id&gt;</code> - List channels<br>
            <code>!guilds</code> - List servers<br>
            <code>!leave_guild &lt;id&gt;</code> - Leave server<br>
            <code>!create_invite &lt;channel_id&gt; [max_uses] [max_age]</code><br>
            <code>!trust add/remove/list &lt;id&gt;</code> - Manage trusted users</p>
        </div>
        <div class="card">
            <h2>💬 AI Commands (natural language)</h2>
            <p>You can also talk to the AI directly! Just type a message and the AI will respond.<br>
            <strong>Example:</strong> "Send a message to my friend John" (if you know their ID)<br>
            <strong>Example:</strong> "Play my favorite song"<br>
            <strong>Example:</strong> "Who is online?"</p>
        </div>
        <script>
            async function fetchData() {{
                try {{
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    document.getElementById('stats').innerHTML = `
                        <p>📨 Messages: <span class="stat-value">${{data.stats.messages_processed || 0}}</span></p>
                        <p>💬 Replies: <span class="stat-value">${{data.stats.responses_sent || 0}}</span></p>
                        <p>🧠 Facts: <span class="stat-value">${{data.stats.facts_extracted || 0}}</span></p>
                        <p>🚫 Blocked: <span class="stat-value">${{(data.stats.toxic_blocked || 0) + (data.stats.spam_blocked || 0)}}</span></p>
                    `;
                    document.getElementById('voice').innerHTML = `
                        <p>🎧 Connected: ${{data.voice.connected ? '✅ Yes' : '❌ No'}}</p>
                        ${{data.voice.playing ? `<p>🎵 Now playing: <strong>${{data.voice.title}}</strong></p>` : ''}}
                        <p>📊 Channel: ${{data.voice.channel || 'N/A'}}</p>
                    `;
                }} catch(e) {{
                    document.getElementById('stats').innerText = 'Error loading data.';
                }}
            }}
            fetchData();
            setInterval(fetchData, 15000);
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

async def start_dashboard():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/set_token', set_token)
    app.router.add_get('/api/status', api_status)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=config.WEB_HOST, port=config.WEB_PORT)
    await site.start()
    logger.info(f"🌐 Dashboard running on http://{config.WEB_HOST}:{config.WEB_PORT}")
