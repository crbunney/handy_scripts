"""Sends a number of requests to a URL and records the time taken to complete them, saving the times to a file"""
import statistics
from datetime import timedelta, datetime

import requests
import time

start = time.time()
output_file = 'output.csv'

max_samples = 1000
timings = []

print('[{}] Writing samples to {}'.format(datetime.now(), output_file))
with open(output_file, 'a+') as f:
    f.seek(0)  # We want to read from start of file to count existing samples
    existing_samples = len(f.readlines())
    remaining_samples = max_samples - existing_samples
    print('[{}] existing_samples={}; remaining_samples={}, max_samples={}'.format(
        datetime.now(), existing_samples, remaining_samples, max_samples))
    for sample_count in range(remaining_samples):
        try:
            r = requests.get('some url')
            if r.status_code != 200:
                print('[{}] !!!! HTTP error? !!!'.format(datetime.now()))
                print(r.headers)
                break
            timings.append(r.elapsed.total_seconds())
            f.write(str(r.elapsed.total_seconds()) + '\n')
            if sample_count and sample_count % 100 == 0:
                # This if block is optional, but it's nice to have an idea of progress whilst it's running
                print(f'[{datetime.now()}] {sample_count} samples taken '
                      f'[Overall: {sample_count + existing_samples}/{max_samples}]')
                f.flush()
        except Exception as e:
            print('[{}] !!! Exception !!!'.format(datetime.now()))
            print(e)
        except KeyboardInterrupt:
            print(f'[{datetime.now()}] User aborted')
            break

if timings:
    print()
    print()
    print(f'[{datetime.now()}] Finished in {(time.time() - start)} seconds')
    print('\t'.join(map(str, [timedelta(seconds=sum(timings)), min(timings), max(timings), statistics.mean(timings),
                              statistics.stdev(timings)])))
