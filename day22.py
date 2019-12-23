#!/usr/bin/env python3

import sys
from enum import Enum


class Shuffle(Enum):
    DEAL = 0
    CUT = 1
    DEAL_INCREMENT = 2


def deal(cards):
    return cards[::-1]


def cut(cards, n):
    return cards[n:] + cards[:n]


def deal_increment(cards, n):
    stack = [0] * len(cards)
    for index, card in enumerate(cards):
        stack[(index * n) % len(cards)] = card
    return stack


def parse_shuffles(file):
    shuffle = []
    for line in file:
        expr, num = line.strip().rsplit(' ', 1)
        if expr == 'deal into new':
            shuffle.append((Shuffle.DEAL, 0))
        elif expr == 'cut':
            shuffle.append((Shuffle.CUT, int(num, 10)))
        elif expr == 'deal with increment':
            shuffle.append((Shuffle.DEAL_INCREMENT, int(num, 10)))
    return shuffle


def part1(file):
    cards = range(10007)
    for shuffle, count in parse_shuffles(file):
        if shuffle is Shuffle.DEAL:
            cards = deal(cards)
        elif shuffle is Shuffle.CUT:
            cards = cut(cards, count)
        else:
            cards = deal_increment(cards, count)

    target = 2019
    answer = cards.index(target)
    print(f"Answer: {answer}")


def part2(file):
    # TOOD: Second part of day
    pass


def main(part, file):
    if file.isatty():
        print("Awaiting input from stdin...")

    if part == 1:
        part1(file)
    elif part == 2:
        part2(file)


if __name__ == "__main__":
    if (len(sys.argv) < 2 or len(sys.argv) > 3 or (sys.argv[1] != "1" and sys.argv[1] != "2")):
        print(f"usage: {sys.argv[0]} part [filename]")
        print(f"")
        exit(1)

    input_file = sys.stdin

    if (len(sys.argv) == 3):
        try:
            filename = sys.argv[2]
            input_file = open(filename)
        except FileNotFoundError as e:
            print(e)
            exit(1)

    with input_file:
        main(int(sys.argv[1], 10), input_file)
