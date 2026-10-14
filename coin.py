"""
coin.py  -  Session 04: Expected value, variance & Kelly
Le Moyne College Quantitative Finance Society

A coin that lands your way 60% of the time and pays even money. The edge is
obvious. The question this file answers is the one people get wrong:

    How much of your bankroll should you bet on each flip?

    RUN IT     Change MY_FRACTION (your secret bet size) and run the file.
    CHANGE IT  Fill in the three TODOs.
    EXTEND IT  Scroll to the bottom: find the best fraction over 1,000 runs.

This file also contains random_walk_prices(): fake stock prices made of coin
flips. Keep it. Session 08 uses it to catch your backtester lying.

Run it:  python coin.py      (in Colab:  %run coin.py)
"""
import numpy as np
import pandas as pd

from pot_odds import expected_value          # last week's file, still useful

# ------------------------------------------------------------------ RUN IT
MY_FRACTION = 0.10   # your secret bet size for the tournament: 0.10 = 10% a flip
P_WIN = 0.60         # chance each flip goes your way
ROUNDS = 50          # flips for the four-team race
TOURNAMENT_ROUNDS = 100
START = 100.0        # chips everyone starts with
TEAMS = [0.05, 0.20, 0.50, 1.00]   # the four bet sizes in the race
SEED = 2026          # everyone uses the same seed, so everyone sees the same flips


# --------------------------------------------------------------- the coin
def flips(p_win, n, seed=SEED):
    """n coin flips. True means you won that flip."""
    rng = np.random.default_rng(seed)
    return rng.random(n) < p_win


def play(fraction, outcomes, start=START):
    """
    Bet `fraction` of your CURRENT bankroll on every flip, at even money.
    Returns your bankroll after every flip, starting with `start`.
    """
    bankroll = start
    history = [bankroll]
    for won in outcomes:
        bet = fraction * bankroll
        # TODO 1: if you won, add the bet to bankroll. If you lost, take it away.
        raise NotImplementedError("TODO 1: update the bankroll in play()")
        if bankroll < 1:                      # can't bet less than one chip: you're out
            bankroll = 0.0
        history.append(bankroll)
    return history


def longest_losing_streak(outcomes):
    """The most losses in a row anywhere in the sequence."""
    # TODO 2: walk through `outcomes` keeping two numbers: the current run of
    #         losses, and the longest run so far. A win resets the current run.
    raise NotImplementedError("TODO 2: write longest_losing_streak()")


# ----------------------------------------------------------------- sizing
def kelly_fraction(p_win, payout=1.0):
    """
    The growth-maximising bet size.  f* = p - (1 - p) / payout
    At even money (payout = 1) that is 2p - 1, so 60% -> 0.20.
    """
    # TODO 3: one line, straight from the formula above.
    raise NotImplementedError("TODO 3: write kelly_fraction()")


def growth_rate(fraction, p_win, payout=1.0):
    """Average log-growth of the bankroll per flip. Above zero, you get richer."""
    if fraction >= 1:
        return float("-inf")
    return p_win * np.log(1 + fraction * payout) + (1 - p_win) * np.log(1 - fraction)


# --------------------------------------------------- fake prices (session 08)
def random_walk_prices(n_days=1000, tickers=("AAA", "BBB", "CCC"), seed=0,
                       annual_vol=0.20, start_price=100.0):
    """
    Stock prices made of fair coin flips. Every day each ticker goes up or down
    by one day's worth of volatility, 50/50. There is no signal in here.

    Same shape as the qfs-research toolkit's data.synthetic_prices(): a
    DataFrame with business days down the rows and one column per ticker.
    Any rule that "works" on this is fooling you.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    rng = np.random.default_rng(seed)
    daily_vol = annual_vol / np.sqrt(252)
    ups = rng.random((n_days, len(tickers))) < 0.5
    steps = np.where(ups, daily_vol, -daily_vol)
    prices = start_price * np.exp(np.cumsum(steps, axis=0))
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    return pd.DataFrame(prices, index=dates, columns=list(tickers))


# ------------------------------------------------------------------ main
def _skip(err):
    print(f"   ...skipped: {err}")


def main():
    ev = expected_value(P_WIN, 1, 1)
    print(f"\nA {P_WIN:.0%} coin at even money: EV = {ev:+.2f} chips per chip bet.")
    print("Every bet size below has positive EV on every flip. Watch what happens anyway.\n")

    outcomes = flips(P_WIN, ROUNDS)
    paths = {}
    try:
        print(f"{'Bet size':>9}{'Round 10':>11}{'Round 25':>11}{'Round 50':>11}")
        for f in TEAMS:
            paths[f] = play(f, outcomes)
            p = paths[f]
            print(f"{f:>9.0%}" + "".join(f"{p[r]:>11,.0f}" for r in (10, 25, 50)))
    except NotImplementedError as err:
        _skip(err)

    try:
        long_run = flips(P_WIN, 1000, seed=SEED + 1)
        print(f"\nLongest losing streak in 1,000 flips of a {P_WIN:.0%} coin: "
              f"{longest_losing_streak(long_run)} in a row")
    except NotImplementedError as err:
        _skip(err)

    try:
        k = kelly_fraction(P_WIN)
        print(f"\nKelly says bet {k:.0%} of your bankroll. Half Kelly is {k / 2:.0%}.")
        for f in (k / 2, k, 2 * k):
            print(f"   bet {f:>4.0%}: growth {growth_rate(f, P_WIN):+.4f} per flip")
    except NotImplementedError as err:
        _skip(err)

    try:
        final = play(MY_FRACTION, flips(P_WIN, TOURNAMENT_ROUNDS))[-1]
        print(f"\nTOURNAMENT: your secret fraction {MY_FRACTION:.0%} turned 100 chips into "
              f"{final:,.0f} after {TOURNAMENT_ROUNDS} flips.")
        print("Write both numbers on the board.")
    except NotImplementedError as err:
        _skip(err)

    plot(paths)


def plot(paths):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    colours = ["#1B5E43", "#C9A227", "#8C3B2E", "#5C6B63"]

    ax = axes[0]
    for (f, p), c in zip(paths.items(), colours):
        label = f"bet {f:.0%}" + (" (bust)" if p[-1] == 0 else "")
        ax.plot([max(x, 0.5) for x in p], color=c, lw=2, label=label)
    ax.set_yscale("log")
    ax.set_title("Same flips, different bet sizes")
    ax.set_xlabel("Flip")
    ax.set_ylabel("Bankroll (log scale)")
    if paths:
        ax.legend()

    ax = axes[1]
    fs = np.linspace(0, 0.6, 61)
    ax.plot(fs * 100, [growth_rate(f, P_WIN) for f in fs], color="#1B5E43", lw=2)
    ax.axhline(0, color="#5C6B63", lw=1)
    ax.set_title(f"Growth per flip, {P_WIN:.0%} coin")
    ax.set_xlabel("Bet size (% of bankroll)")
    ax.set_ylabel("Average log growth")

    ax = axes[2]
    px = random_walk_prices(n_days=500, tickers=["A", "B", "C", "D"], seed=7)
    for col, c in zip(px.columns, colours):
        ax.plot(px.index, px[col], color=c, lw=1.5)
    ax.set_title("Which one is a real stock? (None. Coin flips.)")
    ax.tick_params(axis="x", labelrotation=30)

    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------- EXTEND IT
#   1. Run every bet size from 0% to 60% on 1,000 different seeds. Plot the
#      MEDIAN final bankroll against bet size. Where is the peak?
#   2. Suppose the coin is really 52/48 but you believe it is 60/40 and bet
#      Kelly for 60/40. What happens to the median? This is what overconfidence
#      in your edge costs.
#   3. Kelly for a bet that pays 2 to 1 and wins 40% of the time?
if __name__ == "__main__":
    main()
