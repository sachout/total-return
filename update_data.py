import datetime, json, os, re, time
import yfinance as yf

tickers = []
for line in open("tickers.txt", encoding="utf-8"):
    t = line.split("#")[0].strip().upper()
    if t and t not in tickers:
        tickers.append(t)

os.makedirs("data", exist_ok=True)
prev = {}
try:
    prev = {x["t"]: x for x in json.load(open("data/index.json", encoding="utf-8"))["tickers"]}
except Exception:
    pass

index = []
for t in tickers:
    try:
        tk = yf.Ticker(t)
        h = tk.history(period="max", auto_adjust=False)  # Close = prix, Adj Close = dividendes réinvestis
        if h.empty:
            print("Introuvable :", t)
            continue
        name = None
        try:
            i = tk.info
            name = i.get("longName") or i.get("shortName")
        except Exception:
            pass
        rows = [[d.strftime("%Y-%m-%d"), round(float(r["Close"]), 4), round(float(r["Adj Close"]), 4)]
                for d, r in h.iterrows() if r["Close"] == r["Close"] and r["Adj Close"] == r["Adj Close"]]
        f = re.sub(r"[^A-Za-z0-9._-]", "_", t) + ".json"
        json.dump({"rows": rows}, open("data/" + f, "w"), separators=(",", ":"))
        index.append({"t": t, "name": name, "file": f})
        print("OK", t, len(rows))
    except Exception as e:
        print("Erreur", t, e)
        if t in prev:
            index.append(prev[t])
    time.sleep(1)

json.dump({"updated": datetime.datetime.utcnow().isoformat() + "Z", "tickers": index},
          open("data/index.json", "w", encoding="utf-8"), ensure_ascii=False)
