"""stocks.txt의 종목 시세·재무지표를 yfinance로 받아 docs/data.json 으로 저장합니다."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
INDICES = {"코스피": "^KS11", "코스닥": "^KQ11"}


def read_list():
    items = []
    for line in (ROOT / "stocks.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            code, _, name = line.partition(" ")
            items.append((code.strip(), name.strip()))
    return items


def closes(ticker, period="1y"):
    df = ticker.history(period=period)
    return [[d.strftime("%Y-%m-%d"), round(float(c), 2)] for d, c in df["Close"].dropna().items()]


def pack(history):
    if len(history) < 2:
        return None, None, None
    price, prev = history[-1][1], history[-2][1]
    return price, prev, round((price / prev - 1) * 100, 2)


def build_stock(code, name):
    for suffix in (".KS", ".KQ"):  # 코스피 → 코스닥 순서로 시도
        t = yf.Ticker(code + suffix)
        h = closes(t)
        if len(h) >= 2:
            break
    else:
        raise ValueError("시세 데이터 없음")
    price, prev, pct = pack(h)
    try:
        info = t.info or {}
    except Exception:
        info = {}
    rate = info.get("dividendRate")
    return {
        "code": code, "name": name or info.get("shortName") or code,
        "price": price, "prev": prev, "change_pct": pct,
        "volume": info.get("volume") or info.get("regularMarketVolume"),
        "per": info.get("trailingPE"), "pbr": info.get("priceToBook"),
        "div_yield": round(rate / price * 100, 2) if rate and price else None,
        "market_cap": info.get("marketCap"),
        "history": h,
    }


def main():
    out = {"updated": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST"),
           "indices": [], "stocks": []}
    for name, sym in INDICES.items():
        try:
            h = closes(yf.Ticker(sym))
            price, prev, pct = pack(h)
            out["indices"].append({"name": name, "price": price, "prev": prev, "change_pct": pct, "history": h})
        except Exception as e:
            print(f"[지수 실패] {name}: {e}", file=sys.stderr)
    for code, name in read_list():
        try:
            out["stocks"].append(build_stock(code, name))
        except Exception as e:
            print(f"[종목 실패] {code}: {e}", file=sys.stderr)
    if not out["stocks"]:
        sys.exit("종목 데이터를 하나도 받지 못해 data.json을 갱신하지 않습니다.")
    (ROOT / "docs" / "data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"완료: 종목 {len(out['stocks'])}개, 지수 {len(out['indices'])}개")


if __name__ == "__main__":
    main()
