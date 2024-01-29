from locust import HttpUser, task


class CurrencyPairs(HttpUser):
    @task
    def currency_pairs(self):
        tokens = ['btc', 'eth','a']
        currencies = ['rub', 'usd','b']
        for token in tokens:
            for currency in currencies:
                self.client.get(f"/api/v1/courses?token={token}&currency={currency}")
