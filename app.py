from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import json
import traceback

app = Flask(__name__)
CORS(app)

session = requests.Session()
cache = {"data": [], "timestamp": 0}
CACHE_TTL = 30

@app.route('/api/markets')
def get_markets():
    if time.time() - cache["timestamp"] < CACHE_TTL:
        return jsonify(cache["data"])

    try:
        res = session.get(
            "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=30",
            timeout=10
        )
        res.raise_for_status()
        raw_data = res.json()

        markets = []
        for m in raw_data:
            tokens = m.get("tokens", [])

            yes_price = 0.0
            no_price = 0.0

            try:
                if tokens and len(tokens) >= 2:
                    yes_price = float(tokens[0].get("price", 0) or 0)
                    no_price = float(tokens[1].get("price", 0) or 0)
                elif "outcomePrices" in m and m.get("outcomePrices"):
                    prices = json.loads(m["outcomePrices"])
                    yes_price = float(prices[0]) if len(prices) > 0 else 0.0
                    no_price = float(prices[1]) if len(prices) > 1 else 0.0
                else:
                    yes_price = float(m.get("bestBid", 0) or 0)
                    no_price = 1 - yes_price if yes_price <= 1 else 0.0
            except Exception:
                yes_price = 0.0
                no_price = 0.0

            clob_token_ids = []
            if m.get("clobTokenIds"):
                try:
                    clob_token_ids = json.loads(m.get("clobTokenIds", "[]"))
                except Exception:
                    clob_token_ids = []

            yes_token_id = clob_token_ids[0] if len(clob_token_ids) > 0 else ""
            no_token_id = clob_token_ids[1] if len(clob_token_ids) > 1 else ""

            resolution = "pending"
            if m.get("closed"):
                if yes_price > no_price:
                    resolution = "yes"
                elif no_price > yes_price:
                    resolution = "no"
                else:
                    resolution = "closed"

            markets.append({
                "id": yes_token_id,
                "conditionId": m.get("conditionId", ""),
                "yesTokenId": yes_token_id,
                "noTokenId": no_token_id,
                "title": m.get("question", "Unknown Market"),
                "yes": yes_price,
                "no": no_price,
                "image": m.get("image", ""),
                "pool": float(m.get("volumeNum", 0) or 0),
                "total": yes_price + no_price,
                "description": m.get("description", ""),
                "status": "closed" if m.get("closed") else "active",
                "resolution": resolution
            })

        cache["data"] = markets
        cache["timestamp"] = time.time()
        return jsonify(markets)

    except Exception as e:
        print(f"/api/markets 错误: {e}")
        traceback.print_exc()
        if cache["data"]:
            return jsonify(cache["data"])
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<token_id>')
def get_history(token_id):
    try:
        range_hours = request.args.get("range", "24")
        if range_hours not in ["24", "72"]:
            range_hours = "24"

        fidelity = 24 if range_hours == "24" else 72

        res = session.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": token_id,
                "interval": "1h",
                "fidelity": fidelity
            },
            timeout=10
        )
        res.raise_for_status()
        data = res.json()

        history = []
        if "history" in data and isinstance(data["history"], list):
            for point in data["history"]:
                history.append({
                    "timestamp": point.get("t", 0),
                    "price": float(point.get("p", 0) or 0)
                })

        return jsonify(history)

    except Exception as e:
        print(f"/api/history 错误: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
