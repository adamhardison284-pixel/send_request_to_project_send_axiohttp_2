import asyncio
import aiohttp
import time

API_URLS = [
    "https://lezrsmwspvrdahngtvli.supabase.co/functions/v1/PojectSend",
    "https://vuudkapcuwtkepeqkpfx.supabase.co/functions/v1/PojectSend",
    "https://guypgtlqmsoyjvsspfro.supabase.co/functions/v1/PojectSend",
    "https://neighiwqhabqzhakwupe.supabase.co/functions/v1/PojectSend",
    "https://gmweskylxvbhhgrcftbo.supabase.co/functions/v1/PojectSend",
]

TOTAL_WORKERS = 25
GROUP_SIZE = 5
INTERVAL = 2
RUN_DURATION = 600 # 10 minutes

async def worker(session, worker_id, url):
    counter = 0
    end_time = time.time() + RUN_DURATION

    while True:
        counter += 1
        cron_id = f"worker_google_{worker_id}_{counter}"

        try:
            async with session.post(
                url,
                json={"source": "github_cron", "cron_id": cron_id}
            ) as resp:
                text = await resp.text()
                print(f"{cron_id} {resp.status}")
                print(text)
                print("=" * 80)

        except Exception as e:
            print(f"{cron_id} ERROR: {e}")

        await asyncio.sleep(INTERVAL)

async def main():
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []

        for i in range(TOTAL_WORKERS):
            group = i // GROUP_SIZE
            url = API_URLS[group % len(API_URLS)]

            tasks.append(
                asyncio.create_task(worker(session, i, url))
            )

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
