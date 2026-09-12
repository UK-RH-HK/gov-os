"""Entry point for shipping-quotes."""
from app.retry import with_retry
from app.billing import quote_price
from app.config import GATEWAY_URL


def main() -> str:
    price = with_retry(lambda: quote_price(weight_kg=2.0, zone="B"))
    return f"{GATEWAY_URL}: {price}"


if __name__ == "__main__":
    print(main())
