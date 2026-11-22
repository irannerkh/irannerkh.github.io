import re, json, base64, time, sys, os, urllib.request, urllib.error, datetime

REPO = "irannerkh/irannerkh.github.io"
API = "https://api.github.com/repos/" + REPO
UNION = "https://www.estjt.ir/"
NOBI = "https://apiv2.nobitex.ir/market/udf/history?symbol=USDTIRT&resolution=%s&from=%d&to=%d"
STORE = os.path.expanduser("~/hist_gold18.json")
EVERY = 60
PUSH_EVERY = 1800
OFF = 12600
HDR = {}

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def to_en(s):
    return s.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))

def clean(s):
    s = to_en(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\s+", " ", s.replace("\u200c", " ")).strip()

def gold18_now(html=None):
    html = html or get(UNION)
    for name, price in re.findall(r'<td class="name">(.*?)</td>\s*<td class="price">(.*?)</td>', html, re.S):
        n = clean(name)
        if "18" in n and "عیار" in n:
            d = re.sub(r"\D", "", clean(price))
            if d:
                return int(d)
    return None

def load_store():
    try:
        return {int(k): v for k, v in json.load(open(STORE)).items()}
    except Exception:
        return {}

def save_store(st):
    json.dump({str(k): v for k, v in st.items()}, open(STORE, "w"))

def tick(st, price, now=None):
    now = int(now or time.time())
    b = now // 300 * 300
    c = st.get(b)
    if c:
        c[1] = max(c[1], price); c[2] = min(c[2], price); c[3] = price
    else:
        st[b] = [price, price, price, price]
    for k in [k for k in st if k < now - 14 * 86400]:
        del st[k]

def roll(st, step, offset=0, keep=None):
    out = {}
    for t in sorted(st):
        o, h, l, c = st[t]
        b = (t + offset) // step * step - offset
        if b in out:
            x = out[b]; x[1] = max(x[1], h); x[2] = min(x[2], l); x[3] = c
        else:
            out[b] = [o, h, l, c]
    rows = [[b] + v for b, v in sorted(out.items())]
    return rows[-keep:] if keep else rows

def nobi(res, days):
    now = int(time.time())
    j = json.loads(get(NOBI % (res, now - days * 86400, now), {"User-Agent": "TraderBot/irannerkh"}))
    if j.get("s") != "ok":
        raise Exception("nobitex: " + str(j)[:100])
    rows = [[int(t), float(o), float(h), float(l), float(c)] for t, o, h, l, c in zip(j["t"], j["o"], j["h"], j["l"], j["c"])]
    if rows and rows[-1][4] > 1500000:
        rows = [[r[0]] + [v / 10 for v in r[1:]] for r in rows]
    return [[r[0]] + [round(v) for v in r[1:]] for r in rows]

def build(st):
    g = {"5": roll(st, 300, 0, 288), "60": roll(st, 3600, 0, 336), "D": roll(st, 86400, OFF, 180)}
    try:
        t = {"5": nobi("5", 1), "60": nobi("60", 14), "D": nobi("D", 180)}
    except Exception as e:
        print(time.strftime("%H:%M"), "خطا (تتر):", e)
        t = {}
    return {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "gold18": g, "tether": t}

def api(method, path, body=None):
    req = urllib.request.Request(API + path, data=(json.dumps(body).encode() if body is not None else None), headers=HDR, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}

def ensure_branch():
    try:
        api("GET", "/git/ref/heads/data")
        return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    sha = api("GET", "/git/ref/heads/main")["object"]["sha"]
    api("POST", "/git/refs", {"ref": "refs/heads/data", "sha": sha})

def put(text):
    for i in range(4):
        try:
            try:
                sha = api("GET", "/contents/charts.json?ref=data")["sha"]
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
                sha = None
            body = {"message": "charts", "branch": "data", "content": base64.b64encode(text.encode()).decode()}
            if sha:
                body["sha"] = sha
            api("PUT", "/contents/charts.json", body)
            return
        except urllib.error.HTTPError as e:
            if e.code in (409, 422) and i < 3:
                time.sleep(3)
                continue
            raise

def run():
    global HDR
    token = open(os.path.expanduser("~/.gh_token")).read().strip()
    HDR = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "User-Agent": "irannerkh-charts"}
    st = load_store()
    last_push = 0
    while True:
        try:
            p = gold18_now()
            if p and 1000000 < p < 500000000:
                tick(st, p); save_store(st)
        except Exception as e:
            print(time.strftime("%H:%M"), "خطا (طلا):", e)
        if time.time() - last_push >= PUSH_EVERY:
            try:
                ensure_branch()
                put(json.dumps(build(st), separators=(",", ":")))
                last_push = time.time()
                print(time.strftime("%H:%M"), "نمودارها ارسال شد", len(st), "شمع ۵دقیقه‌ای طلا")
            except Exception as e:
                print(time.strftime("%H:%M"), "خطا (ارسال):", e)
                last_push = time.time() - PUSH_EVERY + 300
        time.sleep(EVERY)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("طلای ۱۸ اتحادیه:", gold18_now())
        for res, d in (("5", 1), ("60", 2), ("D", 5)):
            rows = nobi(res, d)
            print("تتر", res, len(rows), "شمع؛ آخرین:", rows[-1] if rows else None)
    else:
        run()
