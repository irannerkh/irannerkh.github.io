import re, json, base64, time, sys, os, urllib.request, urllib.error, datetime

REPO = "irannerkh/irannerkh.github.io"
SRC = "https://www.estjt.ir/"
EVERY = 60
MIN_GAP = 120
KEEPALIVE = 600
MAIN_GAP = 1800
API = "https://api.github.com/repos/" + REPO
FILE = "union.json"
HDR = {}

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

FA = "۰۱۲۳۴۵۶۷۸۹"
def to_en(s):
    return s.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
def to_fa(s):
    return s.translate(str.maketrans("0123456789", FA))

def clean(s):
    s = to_en(re.sub(r"<[^>]+>", "", s))
    s = s.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    return re.sub(r"\s+", " ", s).strip()

def to_amount(s):
    s = re.sub(r"\s+", "", clean(s))
    m = re.search(r"[٫.](\d{1,2})$", s)
    if m:
        ip = re.sub(r"\D", "", s[:m.start()])
        return float((ip or "0") + "." + m.group(1))
    d = re.sub(r"\D", "", s)
    return float(d) if d else None

def key_of(n):
    if "اونس" in n: return "ounce"
    if "مظنه" in n: return "mazaneh"
    if "18" in n and "عیار" in n: return "gold18"
    if "24" in n and "عیار" in n: return "gold24"
    if "طرح جدید" in n: return "coin_new"
    if "طرح قدیم" in n: return "coin_old"
    if "نیم" in n: return "nim"
    if "ربع" in n: return "rob"
    if "گرمی" in n: return "gerami"
    return None

def parse(html):
    items, changes = {}, {}
    for row in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        nm = re.search(r'<td class="name">(.*?)</td>', row, re.S)
        pr = re.search(r'<td class="price">(.*?)</td>', row, re.S)
        if not nm or not pr:
            continue
        k = key_of(clean(nm.group(1)))
        digits = re.sub(r"\D", "", clean(pr.group(1)))
        if not k or not digits or k in items:
            continue
        p = int(digits)
        items[k] = p
        ch = re.search(r'<td class="change">(.*?)</td>', row, re.S)
        if ch:
            amt = to_amount(ch.group(1))
            if amt is not None:
                sign = -1 if "angle-down" in ch.group(1) else 1
                prev = p - sign * amt
                if prev > 0 and abs(amt) / prev < 0.15:
                    changes[k] = round(sign * amt / prev * 100, 2)
    upd = ""
    i = html.find("بروزرسانی")
    if i >= 0:
        m = re.search(r"(\d{1,2})\s+(\S+)\s+(\d{4})\s*-\s*(\d{1,2}:\d{2}(?::\d{2})?)", clean(html[i:i + 300]))
        if m:
            upd = to_fa("%s %s %s - %s" % m.groups())
    return items, changes, upd

NOBI_STATS = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"

def tether():
    j = json.loads(get(NOBI_STATS, {"User-Agent": "TraderBot/irannerkh"}))
    st = j["stats"]["usdt-rls"]
    last = float(st["latest"])
    opn = float(st.get("dayOpen") or 0)
    scale = 10 if last > 1500000 else 1
    ch = (last / opn - 1) * 100 if opn > 0 else float(st.get("dayChange") or 0)
    return {"price": round(last / scale), "change": round(ch, 2)}

def sane(it):
    g18, g24 = it.get("gold18"), it.get("gold24")
    if not g18 or not (1000000 < g18 < 500000000):
        return False
    if g24 and abs(g24 * 0.75 / g18 - 1) > 0.05:
        return False
    return True

def api(method, path, body=None):
    req = urllib.request.Request(API + path, data=(json.dumps(body).encode() if body is not None else None), headers=HDR, method=method)
    with urllib.request.urlopen(req, timeout=25) as r:
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

def put(branch, text):
    try:
        sha = api("GET", "/contents/%s?ref=%s" % (FILE, branch))["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        sha = None
    body = {"message": "union prices", "branch": branch, "content": base64.b64encode(text.encode()).decode()}
    if sha:
        body["sha"] = sha
    api("PUT", "/contents/" + FILE, body)

def run():
    global HDR
    token = open(os.path.expanduser("~/.gh_token")).read().strip()
    HDR = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "User-Agent": "irannerkh-union"}
    last_key, last_data, last_main = None, 0, 0
    last_t, last_t_time = None, 0
    while True:
        try:
            items, changes, upd = parse(get(SRC))
            try:
                last_t, last_t_time = tether(), time.time()
            except Exception as e:
                print(time.strftime("%H:%M"), "خطا (تتر):", e)
            tt = last_t if last_t and time.time() - last_t_time < 600 else None
            if not sane(items):
                print(time.strftime("%H:%M"), "نتیجه نامعتبر:", items)
            else:
                key = json.dumps([items, changes, upd, tt], sort_keys=True)
                now = time.time()
                if (key != last_key and now - last_data >= MIN_GAP) or now - last_data >= KEEPALIVE:
                    data = {"source": "اتحادیه طلا و جواهر تهران", "url": SRC, "updated_fa": upd,
                            "fetched": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "items": items, "changes": changes, "tether": tt}
                    text = json.dumps(data, ensure_ascii=False)
                    ensure_branch()
                    put("data", text)
                    if now - last_main >= MAIN_GAP:
                        put("main", text)
                        last_main = now
                    last_key, last_data = key, now
                    print(time.strftime("%H:%M"), "ارسال شد", items.get("gold18"), upd)
        except Exception as e:
            print(time.strftime("%H:%M"), "خطا:", e)
        time.sleep(EVERY)

if len(sys.argv) > 1 and sys.argv[1] == "test":
    it, ch, up = parse(get(SRC))
    print(json.dumps(it, indent=1)); print("تغییر درصدی:", json.dumps(ch)); print("زمان اتحادیه:", up); print("معتبر:", sane(it))
    try:
        print("تتر نوبیتکس:", tether())
    except Exception as e:
        print("خطا (تتر):", e)
else:
    run()
