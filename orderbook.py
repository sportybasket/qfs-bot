"""
orderbook.py  -  Session 05: What is a market
Le Moyne College Quantitative Finance Society

In session 02 your bot called submit_order() and a share appeared. This file
is what was on the other end: a limit order book. Bids on one side, asks on
the other, matched best price first, then first come first served.

    RUN IT     Change BUY_SIZES and run the file. Watch big orders get expensive.
    CHANGE IT  Fill in the three TODOs.
    EXTEND IT  Scroll to the bottom: cancel orders, then get picked off by news.

Run it:  python orderbook.py      (in Colab:  %run orderbook.py)
"""
import itertools
from dataclasses import dataclass, field

# ------------------------------------------------------------------ RUN IT
BUY_SIZES = [10, 100, 400, 1500]   # market buys to try, in shares
MY_BID = 100.00                    # where you post your own limit order to buy

_next_id = itertools.count(1)


@dataclass
class Order:
    side: str                      # "buy" or "sell"
    price: float
    qty: int
    owner: str = "anon"
    id: int = field(default_factory=lambda: next(_next_id))


class OrderBook:
    def __init__(self):
        self.bids = []             # buy orders, best (highest price) first
        self.asks = []             # sell orders, best (lowest price) first
        self.trades = []           # every fill: (price, qty, buyer, seller)

    # ------------------------------------------------------------ posting
    def add_limit(self, side, price, qty, owner="anon"):
        """
        Post a limit order: "I'll trade, but only at this price or better."
        If it crosses the spread it trades straight away, up to its price.
        Whatever is left over rests in the book and waits.
        """
        fills = self._match(side, qty, limit=price, owner=owner)
        left = qty - sum(q for _, q in fills)
        if left > 0:
            order = Order(side, price, left, owner)
            if side == "buy":
                self.bids.append(order)
                self.bids.sort(key=lambda o: (-o.price, o.id))   # price, then time
            else:
                self.asks.append(order)
                self.asks.sort(key=lambda o: (o.price, o.id))
            fills.append(("resting", order))
        return fills

    def market_order(self, side, qty, owner="anon"):
        """Trade right now, at whatever prices are there. Returns [(price, qty), ...]."""
        return self._match(side, qty, limit=None, owner=owner)

    # -------------------------------------------------------------- quote
    def best_bid(self):
        return self.bids[0].price if self.bids else None

    def best_ask(self):
        return self.asks[0].price if self.asks else None

    def spread(self):
        """Best ask minus best bid. The price of trading right now."""
        if self.best_bid() is None or self.best_ask() is None:
            return None
        # TODO 1: return the best ask minus the best bid (wrap it in round(..., 4)).
        raise NotImplementedError("TODO 1: write spread()")

    def mid(self):
        if self.spread() is None:
            return None
        return (self.best_bid() + self.best_ask()) / 2

    # ------------------------------------------------------------ matching
    def _match(self, side, qty, limit, owner):
        """
        Walk the other side of the book, best price first, until the order is
        filled or the next price is worse than `limit`. Returns [(price, qty), ...].
        """
        other = self.asks if side == "buy" else self.bids
        fills = []
        remaining = qty
        steps = 0
        while remaining > 0 and other:
            steps += 1
            if steps > 1000:
                raise RuntimeError("The matching loop ran 1,000 times. Did you subtract "
                                   "`take` from both remaining and best.qty?")
            best = other[0]
            too_expensive = limit is not None and (
                (side == "buy" and best.price > limit) or
                (side == "sell" and best.price < limit))
            if too_expensive:
                break
            # TODO 2: trade as much as you can at this price level:
            #   take = the smaller of `remaining` and `best.qty`
            #   add (best.price, take) to fills
            #   subtract take from remaining AND from best.qty
            #   if best.qty is now 0, that order is used up: other.pop(0)
            raise NotImplementedError("TODO 2: the matching loop in _match()")
        return fills

    # ------------------------------------------------------------- display
    def show(self, depth=5):
        print(f"\n{'BIDS (buy)':>24}   |   {'ASKS (sell)':<24}")
        print(f"{'owner':>8}{'qty':>7}{'price':>9}   |   {'price':<9}{'qty':<7}{'owner':<8}")
        for i in range(depth):
            b = self.bids[i] if i < len(self.bids) else None
            a = self.asks[i] if i < len(self.asks) else None
            left = f"{b.owner:>8}{b.qty:>7}{b.price:>9.2f}" if b else " " * 24
            right = f"{a.price:<9.2f}{a.qty:<7}{a.owner:<8}" if a else ""
            print(f"{left}   |   {right}")
        try:
            print(f"Quote {self.best_bid():.2f} / {self.best_ask():.2f}   "
                  f"spread {self.spread():.2f}   mid {self.mid():.3f}")
        except NotImplementedError:
            print(f"Quote {self.best_bid():.2f} / {self.best_ask():.2f}   (finish TODO 1 for the spread)")


def average_price(fills):
    qty = sum(q for _, q in fills)
    return sum(p * q for p, q in fills) / qty if qty else None


def slippage(fills, mid, side="buy"):
    """
    Dollars you paid beyond the mid price, across every fill.
    Buying: (price - mid) x qty for each fill. Selling: (mid - price) x qty.
    """
    # TODO 3: add up (price - mid) * qty over every (price, qty) in fills.
    #         For a sell, flip the sign. Bonus: do it in one line with sum().
    raise NotImplementedError("TODO 3: write slippage()")


def sample_book():
    """A made-up stock, QFS, trading around $100. Thick near the middle, thin further out."""
    book = OrderBook()
    for price, qty in [(99.98, 100), (99.97, 200), (99.95, 300), (99.90, 500), (99.75, 800)]:
        book.add_limit("buy", price, qty, owner="MM")
    for price, qty in [(100.02, 100), (100.03, 200), (100.05, 300), (100.10, 500), (100.30, 800)]:
        book.add_limit("sell", price, qty, owner="MM")
    return book


# ------------------------------------------------------------------ main
def _skip(err):
    print(f"   ...skipped: {err}")


def main():
    book = sample_book()
    book.show()

    print(f"\nMARKET BUYS on a fresh book each time")
    print(f"{'Shares':>7}{'Levels hit':>12}{'Avg price':>11}{'Paid vs mid':>13}{'Per share':>11}")
    for size in BUY_SIZES:
        fresh = sample_book()
        try:
            mid = fresh.mid()
            fills = fresh.market_order("buy", size, owner="you")
            got = sum(q for _, q in fills)
            line = f"{got:>7}{len(fills):>12}{average_price(fills):>11.3f}"
            if got < size:
                line += f"   (book ran out after {got})"
            try:
                cost = slippage(fills, mid)
                line += f"{'$' + format(cost, ',.2f'):>13}{cost / got * 100:>10.1f}c"
            except NotImplementedError as err:
                line += "      TODO 3"
            print(line)
        except NotImplementedError as err:
            _skip(err)
            break

    print(f"\nYOU POST A LIMIT BUY: 50 shares at {MY_BID:.2f}")
    try:
        book.add_limit("buy", MY_BID, 50, owner="you")
        book.show(depth=3)
        print("\nA seller hits the bid with a market order for 120 shares...")
        fills = book.market_order("sell", 120, owner="seller")
        print("   fills:", ", ".join(f"{q} @ {p:.2f}" for p, q in fills))
        print("   You were the best bid, so you filled first. Then the market maker.")
    except NotImplementedError as err:
        _skip(err)

    plot_depth(sample_book())


def plot_depth(book):
    """Cumulative shares available as you move away from the middle."""
    import matplotlib.pyplot as plt

    def steps(orders):
        xs, ys, total = [], [], 0
        for o in orders:
            total += o.qty
            xs.append(o.price)
            ys.append(total)
        return xs, ys

    bx, by = steps(book.bids)
    ax_, ay = steps(book.asks)
    plt.figure(figsize=(8, 4.5))
    plt.step(bx, by, where="post", color="#1B5E43", lw=2, label="Bids: shares you could sell into")
    plt.step(ax_, ay, where="post", color="#C9A227", lw=2, label="Asks: shares you could buy")
    plt.xlabel("Price ($)")
    plt.ylabel("Cumulative shares")
    plt.title("Depth: the further from the middle, the more there is, and the worse the price")
    plt.legend()
    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------- EXTEND IT
#   1. Write cancel(order_id): remove a resting order from whichever side it is on.
#   2. Stale quotes. News arrives: QFS is now worth $101. The market maker has
#      not updated. A fast trader buys every ask below $101. How much did the
#      market maker lose, compared with selling at $101?
#   3. The fix: before the news, cancel the MM's asks and repost them around
#      the new value. That race to cancel is why speed is worth money.
if __name__ == "__main__":
    main()
