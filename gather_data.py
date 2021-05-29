import threading
import itertools
import xrequests
from hcaptcha import Solver

solver = Solver(data_dir="./solver-data")
sitekey, host = "45fbc4de-366c-40ef-9274-9f3feca1cd6c", "v3rmillion.net"
thread_count = 100
proxies = None

try:
    with open("proxies.txt") as fp:
        proxies = itertools.cycle(fp.read().splitlines())
except FileNotFoundError:
    print("Use of proxies is recommended. (proxies.txt)")

def gatherer():
    while True:
        http = xrequests.Session(
            proxies={"https": "http://" + next(proxies)} if proxies else {}
        )

        while True:
            try:
                token = solver.get_token(sitekey, host, http_client=http)
                if token:
                    print("Solved challenge!")
            except Exception as err:
                print(f"Gatherer error: {err}!r")

threads = [threading.Thread(target=gatherer)
           for _ in range(thread_count)]
for t in threads:
    t.start()
for t in threads:
    t.join()
