from market_analysis import analyze_token

def send_signal():
    # مثال برای یک توکن خاص (باید از لیست توکن‌های ترند دریافت شود)
    token_id = "bitcoin"  # جایگزین با توکن واقعی
    token_address = "0x..."  # جایگزین با آدرس توکن واقعی در Arbitrum
    analysis = analyze_token(token_id, token_address)
    action = "buy" if analysis["score"] > 80 else "sell" if analysis["score"] < 50 else "hold"
    return {
        "token": analysis["token"],
        "score": analysis["score"],
        "action": action,
        "price": analysis["price"],
        "exit_points": analysis["exit_points"]
    }
