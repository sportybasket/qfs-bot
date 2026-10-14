"""
pot_odds.py  -  Session 03: Probability with games
Le Moyne College Quantitative Finance Society

The question this file answers:

    I'm on a draw. The pot is offering me a price. Do I call or fold?

That is the question a trader asks too: here is a price, here is my estimate
of the probability, is the gap big enough to act on?

    RUN IT     Change POT and TO_CALL below, run the file, read the verdicts.
    CHANGE IT  Fill in the three TODOs. Each one is a few lines.
    EXTEND IT  Scroll to the bottom: a blackjack card counter.

Run it:  python pot_odds.py      (in Colab:  %run pot_odds.py)
"""
import math
import random

# ------------------------------------------------------------------ RUN IT
POT = 80          # dollars already in the pot, including your opponent's bet
TO_CALL = 20      # what it costs you to stay in the hand
TRIALS = 20_000   # how many times the simulation re-deals the rest of the hand
SEED = 3          # same seed = same "random" deals for everyone in the room

# The hands we test. Cards are two characters: rank then suit.
# Ranks 2-9, T (ten), J, Q, K, A.  Suits S, H, D, C.
SCENARIOS = [
    ("Flush draw",            ["AH", "7H"], ["KH", "2H", "9C"]),
    ("Open-ended straight",   ["8S", "9D"], ["TC", "JH", "2S"]),
    ("Gutshot straight",      ["8S", "9D"], ["JC", "QH", "2S"]),
    ("Flush + straight draw", ["8H", "9H"], ["TH", "JC", "2H"]),
]


# --------------------------------------------------------------- the cards
RANKS = "23456789TJQKA"
SUITS = "SHDC"


def new_deck():
    """52 cards as strings: 'AH' is the ace of hearts, 'TC' the ten of clubs."""
    return [r + s for r in RANKS for s in SUITS]


def unseen_cards(seen):
    """Every card you can't see: the ones that might still come."""
    return [c for c in new_deck() if c not in seen]


def flush_outs(hand, board):
    """Cards that complete a flush, if you hold four of one suit."""
    seen = hand + board
    for suit in SUITS:
        if sum(c[1] == suit for c in seen) == 4:
            return [c for c in unseen_cards(seen) if c[1] == suit]
    return []


def _has_straight(ranks):
    return any(all(r + i in ranks for i in range(5)) for r in range(-1, 9))


def straight_outs(hand, board):
    """Cards that complete a straight (five ranks in a row; an ace can be low)."""
    seen = hand + board
    have = {RANKS.index(c[0]) for c in seen}
    if 12 in have:
        have.add(-1)                        # the ace also plays as a one
    if _has_straight(have):
        return []
    outs = []
    for c in unseen_cards(seen):
        r = RANKS.index(c[0])
        extra = {r, -1} if r == 12 else {r}
        if _has_straight(have | extra):
            outs.append(c)
    return outs


def all_outs(hand, board):
    """Flush outs and straight outs together. A set, so no card counts twice."""
    return sorted(set(flush_outs(hand, board)) | set(straight_outs(hand, board)))


# ----------------------------------------------------------- probability
def rule_of_thumb(outs, cards_to_come):
    """Rule of 4 on the flop (two cards to come), rule of 2 on the turn."""
    return outs * (4 if cards_to_come == 2 else 2) / 100


def exact_hit_chance(outs, unseen, cards_to_come):
    """One minus the chance that every card still to come misses."""
    miss = math.comb(unseen - outs, cards_to_come) / math.comb(unseen, cards_to_come)
    return 1 - miss


def simulate_hit_chance(outs, unseen, cards_to_come, trials=TRIALS, seed=SEED):
    """Deal the rest of the hand thousands of times and count how often you hit."""
    rng = random.Random(seed)
    outs = set(outs)
    hits = 0
    for _ in range(trials):
        drawn = rng.sample(unseen, cards_to_come)      # deal the turn and river
        # TODO 3: if any card in `drawn` is one of your `outs`, add 1 to hits.
        #         Hint: `card in outs` is True or False. One or two lines.
        raise NotImplementedError("TODO 3: count the hits in simulate_hit_chance()")
    return hits / trials


# --------------------------------------------------------------- the price
def expected_value(p_win, amount_won, amount_lost):
    """EV = p(win) x amount won  -  p(lose) x amount lost.  Session 04 reuses this."""
    return p_win * amount_won - (1 - p_win) * amount_lost


def pot_odds(pot, to_call):
    """
    The break-even probability: the share of the final pot that your call pays for.
    $20 to call into an $80 pot  ->  20 / (80 + 20)  =  0.20
    """
    # TODO 1: return what you pay divided by the whole pot after you call.
    raise NotImplementedError("TODO 1: write pot_odds()")


def decide(equity, pot, to_call):
    """Returns ("CALL" or "FOLD", the EV of calling in dollars)."""
    # TODO 2: use expected_value() above. If you call and win, you win the pot.
    #         If you call and lose, you lose what you called.
    #         Return ("CALL", ev) when ev is above zero, otherwise ("FOLD", ev).
    raise NotImplementedError("TODO 2: write decide()")


# ------------------------------------------------------------------ main
def _skip(err):
    print(f"   ...skipped: {err}")


def main():
    print(f"\nPOT ${POT}, TO CALL ${TO_CALL}")
    try:
        price = pot_odds(POT, TO_CALL)
        print(f"Break-even: you need to win at least {price:.1%} of the time.\n")
    except NotImplementedError as err:
        _skip(err)
        price = None

    header = f"{'Hand':<24}{'Outs':>5}{'Rule of 4':>11}{'Exact':>8}{'Simulated':>11}   {'Verdict':<8}{'EV of call':>11}"
    print(header)
    print("-" * len(header))
    for name, hand, board in SCENARIOS:
        outs = all_outs(hand, board)
        unseen = unseen_cards(hand + board)
        thumb = rule_of_thumb(len(outs), 2)
        exact = exact_hit_chance(len(outs), len(unseen), 2)
        line = f"{name:<24}{len(outs):>5}{thumb:>11.1%}{exact:>8.1%}"
        try:
            sim = simulate_hit_chance(outs, unseen, 2)
            line += f"{sim:>11.1%}"
        except NotImplementedError:
            line += f"{'TODO 3':>11}"
        try:
            verdict, ev = decide(exact, POT, TO_CALL)
            money = f"{'+' if ev >= 0 else '-'}${abs(ev):.2f}"
            line += f"   {verdict:<8}{money:>11}"
        except NotImplementedError:
            line += f"   {'TODO 2':<8}"
        print(line)

    print("\nOuts are cards that make your hand. They are not guaranteed winners.")
    plot_rule_vs_exact()


def plot_rule_vs_exact():
    """Where does the rule of 4 stop being a good shortcut?"""
    import matplotlib.pyplot as plt

    xs = list(range(1, 21))
    plt.figure(figsize=(8, 4.5))
    plt.plot(xs, [rule_of_thumb(n, 2) * 100 for n in xs], "o-", color="#C9A227", label="Rule of 4")
    plt.plot(xs, [exact_hit_chance(n, 47, 2) * 100 for n in xs], "o-", color="#1B5E43", label="Exact")
    plt.xlabel("Outs (on the flop, two cards to come)")
    plt.ylabel("Chance of hitting (%)")
    plt.title("The rule of 4 is close up to about 10 outs, then it overshoots")
    plt.xticks(xs)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------- EXTEND IT
# Blackjack card counting with Hi-Lo: +1 for 2-6, 0 for 7-9, -1 for tens and aces.
#   1. Write hilo_value(card) and running_count(cards).
#   2. Check that a full shuffled deck always counts back to zero. Why must it?
#   3. Shuffle a six-deck shoe and deal it 52 cards at a time. After each
#      chunk, print the true count = running count / decks left.
#      A high true count means the deck is rich in tens and aces: bet more.
if __name__ == "__main__":
    main()
