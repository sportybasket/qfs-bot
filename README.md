# qfs-bot

The Le Moyne College Quantitative Finance Society semester project. Every
session adds one file. By pitch night it's a small research setup you wrote
yourself.

| Session | File | What it does |
|---|---|---|
| 02 | `first_bot.py` | Places a paper order on Alpaca |
| 03 | `pot_odds.py` | Outs, equity, pot odds: call or fold? |
| 04 | `coin.py` | Bet sizing, Kelly, and fake coin-flip stock prices |
| 05 | `orderbook.py` | A working limit order book |

## Open a session in Colab

Click your session's link, then run the cells top to bottom:

- [Session 03: pot odds](https://colab.research.google.com/github/sportybasket/qfs-bot/blob/main/notebooks/03_pot_odds.ipynb)
- [Session 04: coin](https://colab.research.google.com/github/sportybasket/qfs-bot/blob/main/notebooks/04_coin.ipynb)
- [Session 05: order book](https://colab.research.google.com/github/sportybasket/qfs-bot/blob/main/notebooks/05_orderbook.ipynb)

Each file has 2-3 `# TODO`s. Anything you haven't built yet prints
`...skipped: TODO n` instead of crashing.

**Colab deletes your files when the runtime resets.** Run the last cell to
download your work before you leave.

## Run it on your own machine

```bash
pip install -r requirements.txt
python pot_odds.py
```
