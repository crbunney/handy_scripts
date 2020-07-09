"""Hacky script that sends lots of requests to an endpoint for the purposes of generating lambda invoations to
benchmark performance. Use Cloudwatch insights to query the performance data, this query will help:
filter @type = "REPORT"
| fields @requestId, @timestamp, @memorySize/1000000, @duration/1000, @initDuration/1000, @billedDuration/1000
| limit 10000

Note that the most you can get back in a single query is 10,000 results, so you may need to batch up larger results
sets using the date/time controls in the UI
"""
import asyncio
import logging
from datetime import datetime

import aiohttp
import sys
import time


async def take_sample(session: aiohttp.ClientSession, url='some url'):
    """Send a single HTTP request and report the time taken as measured using the system time"""
    start_time = time.time()  # Is this accurate? probably not, as I doubt it takes into account time spent queuing
    try:
        async with session.get('') as r:
            if r.status != 200:
                raise Exception('[{}] !!!! HTTP error? !!! {}'.format(datetime.now(), r.headers))
            duration = time.time() - start_time
        return duration
    except Exception as e:
        print(e, file=sys.stderr)


async def send_requests(max_requests=5000, batch_size=100, sleep=0):
    """
    Send lots of requests to a URL in batches. Be careful with the batch size, if it's too large things actually go
    slower. The default seems to offer the best results for the original use case
    """
    start = time.time()
    sample_count = 0
    results = []

    while sample_count < max_requests:
        batch_start = time.time()
        batch = min(max_requests - sample_count, batch_size)
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [take_sample(session) for _ in range(batch)]
            batch_results = [r for r in await asyncio.gather(*tasks) if r]  # Filter out None values due to errors
            results.extend(batch_results)
            sample_count += len(batch_results)

        batch_end = time.time()
        print(f'[{datetime.now()}] {sample_count}/{max_requests} complete in {batch_end - batch_start:.2f} seconds. '
              f'({batch_end - start:.2f} Overall)')

        if sleep > 0:
            asyncio.run(asyncio.sleep(sleep))

    return results


if __name__ == '__main__':
    prog_start = time.time()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(send_requests())

    # Zero-sleep to allow underlying connections to close
    asyncio.run(asyncio.sleep(0))

    print(f'[{datetime.now()}] Program completed in {time.time() - prog_start}')
