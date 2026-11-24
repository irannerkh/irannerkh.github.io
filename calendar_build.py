#!/usr/bin/env python3
"""Fetch the weekly economic calendar feed, translate event titles to Persian
and write calendar.json (times are stored in UTC; the page shows Tehran time)."""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

FEEDS = [
    ("https://nfs.faireconomy.media/ff_calendar_thisweek.json", True),
    ("https://nfs.faireconomy.media/ff_calendar_nextweek.json", False),
]
OUT = "calendar.json"

BASE = {
    "CPI": "شاخص قیمت مصرف‌کننده (CPI)",
    "Core CPI": "CPI هسته",
    "CPI Flash Estimate": "شاخص قیمت مصرف‌کننده (برآورد اولیه)",
    "PPI": "شاخص قیمت تولیدکننده (PPI)",
    "Core PPI": "PPI هسته",
    "PCE Price Index": "شاخص قیمت PCE",
    "Core PCE Price Index": "شاخص قیمت PCE هسته",
    "GDP": "تولید ناخالص داخلی (GDP)",
    "Unemployment Rate": "نرخ بیکاری",
    "Non-Farm Employment Change": "تغییر اشتغال غیرکشاورزی (NFP)",
    "ADP Non-Farm Employment Change": "تغییر اشتغال بخش خصوصی ADP",
    "Unemployment Claims": "درخواست‌های بیمه بیکاری",
    "Federal Funds Rate": "نرخ بهره فدرال رزرو",
    "FOMC Statement": "بیانیه FOMC",
    "FOMC Meeting Minutes": "صورتجلسه FOMC",
    "FOMC Press Conference": "نشست خبری FOMC",
    "FOMC Economic Projections": "پیش‌بینی‌های اقتصادی FOMC",
    "Retail Sales": "فروش خرده‌فروشی",
    "Core Retail Sales": "فروش خرده‌فروشی هسته",
    "ISM Manufacturing PMI": "PMI تولیدی ISM",
    "ISM Services PMI": "PMI خدماتی ISM",
    "Manufacturing PMI": "PMI تولیدی",
    "Services PMI": "PMI خدماتی",
    "Composite PMI": "PMI ترکیبی",
    "Crude Oil Inventories": "ذخایر نفت خام",
    "Natural Gas Storage": "ذخایر گاز طبیعی",
    "JOLTS Job Openings": "فرصت‌های شغلی JOLTS",
    "Average Hourly Earnings": "میانگین دستمزد ساعتی",
    "Trade Balance": "تراز تجاری",
    "Current Account": "تراز حساب جاری",
    "Consumer Confidence": "اعتماد مصرف‌کننده",
    "UoM Consumer Sentiment": "احساسات مصرف‌کننده میشیگان",
    "UoM Inflation Expectations": "انتظارات تورمی میشیگان",
    "Existing Home Sales": "فروش خانه‌های موجود",
    "New Home Sales": "فروش خانه‌های نو",
    "Pending Home Sales": "فروش خانه‌های در حال معامله",
    "Building Permits": "پروانه‌های ساختمانی",
    "Housing Starts": "آغاز ساخت مسکن",
    "Durable Goods Orders": "سفارش کالاهای بادوام",
    "Core Durable Goods Orders": "سفارش کالاهای بادوام هسته",
    "Industrial Production": "تولید صنعتی",
    "Factory Orders": "سفارش‌های کارخانه‌ای",
    "Employment Change": "تغییر اشتغال",
    "Claimant Count Change": "تغییر تعداد متقاضیان بیمه بیکاری",
    "Official Bank Rate": "نرخ رسمی بهره بانک انگلستان",
    "MPC Official Bank Rate Votes": "رأی‌های کمیته سیاست پولی بانک انگلستان",
    "Monetary Policy Summary": "خلاصه سیاست پولی",
    "Monetary Policy Statement": "بیانیه سیاست پولی",
    "Monetary Policy Report": "گزارش سیاست پولی",
    "Main Refinancing Rate": "نرخ بهره اصلی بانک مرکزی اروپا",
    "Deposit Facility Rate": "نرخ بهره سپرده بانک مرکزی اروپا",
    "ECB Press Conference": "نشست خبری بانک مرکزی اروپا",
    "ECB Monetary Policy Meeting Accounts": "صورتجلسه سیاست پولی بانک مرکزی اروپا",
    "Ifo Business Climate": "شاخص فضای کسب‌وکار ifo",
    "ZEW Economic Sentiment": "شاخص احساسات اقتصادی ZEW",
    "Cash Rate": "نرخ بهره نقدی",
    "RBA Rate Statement": "بیانیه نرخ بهره بانک مرکزی استرالیا",
    "RBA Press Conference": "نشست خبری بانک مرکزی استرالیا",
    "Official Cash Rate": "نرخ رسمی بهره نیوزیلند (OCR)",
    "RBNZ Rate Statement": "بیانیه نرخ بهره بانک مرکزی نیوزیلند",
    "RBNZ Monetary Policy Statement": "بیانیه سیاست پولی بانک مرکزی نیوزیلند",
    "RBNZ Press Conference": "نشست خبری بانک مرکزی نیوزیلند",
    "BOJ Policy Rate": "نرخ سیاست‌گذاری بانک ژاپن",
    "BOJ Press Conference": "نشست خبری بانک ژاپن",
    "BOJ Outlook Report": "گزارش چشم‌انداز بانک ژاپن",
    "BOC Rate Statement": "بیانیه نرخ بهره بانک کانادا",
    "BOC Press Conference": "نشست خبری بانک کانادا",
    "BOC Monetary Policy Report": "گزارش سیاست پولی بانک کانادا",
    "Overnight Rate": "نرخ بهره شبانه بانک کانادا",
    "SNB Policy Rate": "نرخ سیاست‌گذاری بانک ملی سوئیس",
    "SNB Monetary Policy Assessment": "ارزیابی سیاست پولی بانک ملی سوئیس",
    "SNB Press Conference": "نشست خبری بانک ملی سوئیس",
    "Bank Holiday": "تعطیلی بانکی",
    "Wholesale Inventories": "موجودی انبار عمده‌فروشی",
    "Business Inventories": "موجودی انبار کسب‌وکارها",
    "Import Prices": "قیمت واردات",
    "Core Inflation": "تورم هسته",
    "Unemployment Change": "تغییر بیکاری",
    "Gold Reserves": "ذخایر طلا",
    "Fed Balance Sheet": "ترازنامه فدرال رزرو",
    "Beige Book": "کتاب بژ فدرال رزرو",
    "Treasury Currency Report": "گزارش ارزی خزانه‌داری آمریکا",
}

PRE = {
    "Prelim": "اولیه",
    "Preliminary": "اولیه",
    "Flash": "اولیه (Flash)",
    "Final": "نهایی",
    "Advance": "پیش‌برآورد",
    "Revised": "تجدیدنظرشده",
}
SUF = {"m/m": "ماهانه", "y/y": "سالانه", "q/q": "فصلی"}

COUNTRY = {
    "German": "آلمان",
    "French": "فرانسه",
    "Italian": "ایتالیا",
    "Spanish": "اسپانیا",
    "Swiss": "سوئیس",
    "Canadian": "کانادا",
    "Australian": "استرالیا",
    "Chinese": "چین",
    "Japanese": "ژاپن",
    "UK": "انگلیس",
    "US": "آمریکا",
    "Eurozone": "منطقه یورو",
    "NZ": "نیوزیلند",
}

ROLE = {
    "Fed Chair": "رئیس فدرال رزرو",
    "FOMC Member": "عضو FOMC",
    "ECB President": "رئیس بانک مرکزی اروپا",
    "BOE Gov": "رئیس بانک انگلستان",
    "BOJ Gov": "رئیس بانک ژاپن",
    "RBA Gov": "رئیس بانک مرکزی استرالیا",
    "BOC Gov": "رئیس بانک کانادا",
    "SNB Chairman": "رئیس بانک ملی سوئیس",
    "RBNZ Gov": "رئیس بانک مرکزی نیوزیلند",
    "Treasury Sec": "وزیر خزانه‌داری آمریکا",
}
NAMES = {
    "Powell": "پاول", "Lagarde": "لاگارد", "Bailey": "بیلی", "Ueda": "اوئدا",
    "Bullock": "بولاک", "Macklem": "مک‌کلم", "Waller": "والر", "Williams": "ویلیامز",
    "Bessent": "بسنت", "Schlegel": "اشلگل", "Orr": "اور", "Jefferson": "جفرسون",
    "Bowman": "بومن", "Barr": "بار", "Cook": "کوک", "Logan": "لوگان",
}


def translate(title):
    """Return a Persian title, or None when the event is not fully known."""
    t = title.strip()
    m = re.match(r"^(%s)\s+(.+?)\s+Speaks$" % "|".join(map(re.escape, ROLE)), t)
    if m:
        name = m.group(2)
        return "سخنرانی %s، %s" % (NAMES.get(name, name), ROLE[m.group(1)])
    suf = ""
    m = re.search(r"\s(m/m|y/y|q/q)$", t)
    if m:
        suf = SUF[m.group(1)]
        t = t[: m.start()]
    pre = ""
    m = re.match(r"^(%s)\s+(.+)$" % "|".join(PRE), t)
    if m:
        pre = PRE[m.group(1)]
        t = m.group(2)
    country = ""
    if t not in BASE:
        m = re.match(r"^(%s)\s+(.+)$" % "|".join(COUNTRY), t)
        if m:
            country = COUNTRY[m.group(1)]
            t = m.group(2)
    if t not in BASE:
        return None
    out = BASE[t]
    if pre:
        out += " " + pre
    if suf:
        out += " (%s)" % suf
    if country:
        out = "%s: %s" % (country, out)
    return out


def fetch(url):
    last = None
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (irannerkh calendar bot)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(5 * (i + 1))
    raise RuntimeError("%s: %s" % (url, last))


def to_utc(s):
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    events, seen = [], set()
    for url, required in FEEDS:
        try:
            data = fetch(url)
        except Exception as e:  # noqa: BLE001
            print("fetch failed:", e)
            if required:
                sys.exit(1)
            continue
        for e in data:
            try:
                t = to_utc(e["date"])
            except Exception:  # noqa: BLE001
                continue
            key = (t, e.get("country"), e.get("title"))
            if key in seen:
                continue
            seen.add(key)
            en = (e.get("title") or "").strip()
            events.append({
                "t": t,
                "cur": e.get("country") or "",
                "impact": e.get("impact") or "Low",
                "en": en,
                "fa": translate(en),
                "f": (e.get("forecast") or "").strip(),
                "p": (e.get("previous") or "").strip(),
            })
    if not events:
        print("no events")
        sys.exit(1)
    events.sort(key=lambda x: (x["t"], x["cur"], x["en"]))
    old = None
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8")).get("events")
        except Exception:  # noqa: BLE001
            old = None
    if old == events:
        print("unchanged")
        return
    doc = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Forex Factory",
        "events": events,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    untranslated = sorted({e["en"] for e in events if not e["fa"]})
    print("wrote %d events; untranslated titles: %d" % (len(events), len(untranslated)))
    for u in untranslated:
        print("  -", u)


if __name__ == "__main__":
    main()
