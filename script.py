import asyncio
import aiohttp
import time
import json
import random

API_URLS = [
    "https://lezrsmwspvrdahngtvli.supabase.co/functions/v1/PojectSend",
    #"https://vuudkapcuwtkepeqkpfx.supabase.co/functions/v1/PojectSend",
    "https://guypgtlqmsoyjvsspfro.supabase.co/functions/v1/PojectSend",
    #"https://neighiwqhabqzhakwupe.supabase.co/functions/v1/PojectSend",
    "https://gmweskylxvbhhgrcftbo.supabase.co/functions/v1/PojectSend",
]

TOTAL_WORKERS = 25
INTERVAL = 1  # faster since we dynamically control load

# shared cooldown state
url_next_available = {url: 0 for url in API_URLS}
lock = asyncio.Lock()


async def get_available_url():
    async with lock:
        now = time.time()

        # filter URLs that are ready
        available = [u for u, t in url_next_available.items() if now >= t]

        if not available:
            return None

        # pick randomly (can be improved later)
        return random.choice(available)


async def set_cooldown(url, seconds):
    async with lock:
        url_next_available[url] = time.time() + seconds


async def worker(session, worker_id):
    counter = 0

    while True:
        url = await get_available_url()

        # ⛔ no available URLs → wait a bit
        if not url:
            await asyncio.sleep(1)
            continue

        counter += 1
        cron_id = f"worker_{worker_id}_{counter}"

        try:
            async with session.post(
                url,
                json={"source": "github_cron", "cron_id": cron_id}
            ) as resp:

                text = await resp.text()

                print(f"[{worker_id}] {url} → {resp.status}")
                print(text)
                print("=" * 80)

                # 🔥 handle "no project available"
                if resp.status == 429:
                    try:
                        data = json.loads(text)
                        retry_after = data.get("retry_after_seconds", 10)
                    except:
                        retry_after = 10

                    await set_cooldown(url, retry_after)
                    print(f"⏳ {url} cooling down for {retry_after}s")

        except Exception as e:
            print(f"[{worker_id}] ERROR: {e}")

        await asyncio.sleep(INTERVAL)


async def main():
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [
            asyncio.create_task(worker(session, i))
            for i in range(TOTAL_WORKERS)
        ]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
