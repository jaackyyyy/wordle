#!/usr/bin/env python3
import json
import os
import random
import sys

from words import WORDS

STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")
MAX_GUESSES = 6
WORD_LEN = 5

# ANSI colors
GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[97m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

VALID_WORDS = set(w.lower() for w in WORDS if len(w) == WORD_LEN)


def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"played": 0, "won": 0, "streak": 0, "best_streak": 0, "guesses": {}}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def color_guess(guess, target):
    result = []
    target_chars = list(target)
    colored = [""] * WORD_LEN
    used = [False] * WORD_LEN

    # First pass: greens
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            colored[i] = GREEN + f" {g.upper()} " + RESET
            used[i] = True
            target_chars[i] = None

    # Second pass: yellows and grays
    for i, g in enumerate(guess):
        if colored[i]:
            continue
        if g in target_chars:
            idx = target_chars.index(g)
            target_chars[idx] = None
            colored[i] = YELLOW + f" {g.upper()} " + RESET
        else:
            colored[i] = GRAY + f" {g.upper()} " + RESET

    return "".join(colored)


def show_keyboard(guesses, target):
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    letter_state = {}

    for guess in guesses:
        for i, (g, t) in enumerate(zip(guess, target)):
            if g == t:
                letter_state[g] = "green"
            elif g in target and letter_state.get(g) != "green":
                letter_state[g] = "yellow"
            elif g not in letter_state:
                letter_state[g] = "gray"

    print()
    for row in rows:
        print("  ", end="")
        for ch in row:
            state = letter_state.get(ch)
            if state == "green":
                print(GREEN + f" {ch.upper()} " + RESET, end="")
            elif state == "yellow":
                print(YELLOW + f" {ch.upper()} " + RESET, end="")
            elif state == "gray":
                print(GRAY + f" {ch.upper()} " + RESET, end="")
            else:
                print(f" {ch.upper()} ", end="")
        print()
    print()


def show_stats(stats):
    played = stats["played"]
    won = stats["won"]
    pct = int(won / played * 100) if played else 0
    print(f"\n{BOLD}── Statistics ──{RESET}")
    print(f"  Played: {played}  |  Win%: {pct}%  |  Streak: {stats['streak']}  |  Best: {stats['best_streak']}")

    dist = stats.get("guesses", {})
    if dist:
        max_count = max(dist.values(), default=1)
        print(f"\n{BOLD}  Guess distribution:{RESET}")
        for n in range(1, MAX_GUESSES + 1):
            count = dist.get(str(n), 0)
            bar = "█" * int(count / max_count * 12) if max_count else ""
            print(f"  {n} │ {bar} {count}")
    print()


def play_game():
    target = random.choice([w for w in WORDS if len(w) == WORD_LEN]).lower()
    guesses = []
    won = False

    print(f"\n{BOLD}  W O R D L E{RESET}")
    print(f"{DIM}  Guess the 5-letter word in {MAX_GUESSES} tries.{RESET}")
    print(f"{DIM}  {GREEN}   {RESET} correct  {YELLOW}   {RESET} wrong spot  {GRAY}   {RESET} not in word\n{RESET}")

    while len(guesses) < MAX_GUESSES:
        try:
            raw = input(f"  Guess {len(guesses)+1}/{MAX_GUESSES}: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Goodbye!")
            sys.exit(0)

        if raw == ":q" or raw == "quit":
            print(f"\n  The word was {BOLD}{target.upper()}{RESET}. Better luck next time!")
            sys.exit(0)

        if raw == ":s" or raw == "stats":
            show_stats(load_stats())
            continue

        if len(raw) != WORD_LEN:
            print(f"  {DIM}Please enter a {WORD_LEN}-letter word.{RESET}")
            continue

        if raw not in VALID_WORDS:
            print(f"  {DIM}Not in word list.{RESET}")
            continue

        guesses.append(raw)

        print()
        for g in guesses:
            print("  " + color_guess(g, target))
        print()

        show_keyboard(guesses, target)

        if raw == target:
            won = True
            break

    return won, target, len(guesses)


def main():
    print(f"\n{DIM}  Type a 5-letter word to guess. ':q' to quit, ':s' for stats.{RESET}")

    while True:
        stats = load_stats()
        won, target, num_guesses = play_game()

        stats["played"] += 1
        if won:
            stats["won"] += 1
            stats["streak"] += 1
            stats["best_streak"] = max(stats["streak"], stats["best_streak"])
            key = str(num_guesses)
            stats["guesses"][key] = stats["guesses"].get(key, 0) + 1
            lines = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
            print(f"\n  {BOLD}{lines[num_guesses-1]}{RESET}  The word was {GREEN} {target.upper()} {RESET}\n")
        else:
            stats["streak"] = 0
            print(f"\n  The word was {BOLD}{target.upper()}{RESET}. Better luck next time!\n")

        save_stats(stats)
        show_stats(stats)

        try:
            again = input("  Play again? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if again in ("n", "no"):
            print("  Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()
