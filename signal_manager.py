from market_analysis import MarketAnalyzer

class SignalManager:
    def __init__(self, market_data, wallet):
        self.market_data = market_data
        self.wallet = wallet

    def generate_signal(self):
        token = self.market_data["token"]
        score = self.market_data["score"]
        action = "buy" if score > 80 else "sell" if score < 50 else "hold"
        price = self.market_data["price"]
        exit_points = self.market_data["exit_points"]
        return f"سیگنال برای {token}: {action}\nامتیاز: {score}\nقیمت: {price}\nنقاط خروج: {exit_points}"

    @staticmethod
    def send_signal(token_id, token_address):
        analyzer = MarketAnalyzer()
        market_data = analyzer.analyze_token(token_id, token_address)
        return market_data
