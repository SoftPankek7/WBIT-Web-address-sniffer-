import os
os.system('clear' if os.name == 'posix' else 'cls')
print("WB IT! Web Bruteforcing Tool is running.")
print("[i] Loading modules...")
try:
    import requests
except ModuleNotFoundError:
    print("[E] Please install or fix the requests module.")
    exit(2)
import itertools
import string
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("[E] Please install or fix the tqdm module.")
    exit(2)
import threading
import queue
print("[i] Loading variables...")
COMMON_KEYWORDS = [
    "admin", "login", "test", "backup", "api", "old", "dev",
    "config", "upload", "downloads", "db", "server", "private",
    "secret", "hidden", "data", "tmp", "include", "lib"
]
COMMON_EXTENSIONS = ["", "/", ".php", ".html", ".bak", ".zip", ".tar.gz", ".txt", ".iso", ".css", ".js", ".md", ".mp4", ".mp3"]
CHARSET = string.ascii_lowercase + string.digits
MAX_THREADS = 20
TIMEOUT = 5
MAX_LENGTH = 2
print("[i] Starting thread queue...")
task_queue = queue.Queue()
found_results = []
progress_lock = threading.Lock()
print("[i] Loading functions...")
def dynamic_generator(max_length):
    for keyword in COMMON_KEYWORDS:
        for ext in COMMON_EXTENSIONS:
            yield keyword + ext
    for length in range(1, max_length + 1):
        for combo in itertools.product(CHARSET, repeat=length):
            base = ''.join(combo)
            for ext in COMMON_EXTENSIONS:
                yield base + ext
def is_wildcard_response(base_url, test_string="kjkjnlnldnlkdjalkajdlkajdalkjdlkdjsalkjldjladdlkjdsad"):
    test_url = urljoin(base_url, test_string)
    try:
        response = requests.get(test_url, timeout=TIMEOUT)
        return response.status_code, response.text[:200]
    except:
        return None, None
def worker(base_url, wildcard_status, wildcard_content, pbar):
    while True:
        try:
            path = task_queue.get(timeout=1)
        except queue.Empty:
            break
        url = urljoin(base_url, path)
        try:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=False)
            if response.status_code in [200, 403, 401]:
                if not (response.status_code == wildcard_status and response.text[:200] == wildcard_content):
                    result = f"[{response.status_code}] {url}"
                    with progress_lock:
                        tqdm.write(result)
                        found_results.append(result)
        except:
            pass
        finally:
            pbar.update(1)
            task_queue.task_done()
def brute_force(base_url, max_length):
    print("[*] Detecting wildcard 404 behavior...")
    wildcard_status, wildcard_content = is_wildcard_response(base_url)
    if wildcard_status is None:
        print("[W] Couldn't determine wildcard behavior. Continuing blindly.")
    else:
        print(f"[i] Wildcard status detected as {wildcard_status}")

    print("[*] Starting bruteforce...\n")
    with tqdm(desc="Bruteforcing", unit="req", leave=True, colour="Blue") as pbar:
        threads = []
        for _ in range(MAX_THREADS):
            t = threading.Thread(target=worker, args=(base_url, wildcard_status, wildcard_content, pbar))
            t.daemon = True
            t.start()
            threads.append(t)
        for path in dynamic_generator(max_length):
            task_queue.put(path)
            pbar.total = pbar.total + 1 if pbar.total else 1
        task_queue.join()
        for t in threads:
            t.join()
    return found_results
print("[i] WB IT! Made by Softpankek.")
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="WB IT!", description="Webserver Bruteforcer Internet Tool", epilog="Generic usage: appname.exe https://example.com/ --maxlen 2")
    parser.add_argument("url", help="Target base URL (e.g., https://example.com/, 127.0.0.1)")
    parser.add_argument("--maxlen", type=int, default=2, help="Max length of brute-forced names (default: 2)")
    args = parser.parse_args()
    base_url = args.url if args.url.endswith("/") else args.url + "/"
    results = brute_force(base_url, args.maxlen)
    print("\n" + "=" * 50)
    print("\n  Bruteforce Completed")
    print(f"  Found {len(results)} valid path(s):\n")
    for r in results:
        print(r)
    print("=" * 50)
