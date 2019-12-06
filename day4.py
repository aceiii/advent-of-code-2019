#!/usr/bin/env python3

import sys


def match_rules1(val):
    digits = list(map(int, str(val)))
    has_adj_duplicate = False

    for index in range(1, len(digits)):
        current = digits[index]
        previous = digits[index - 1]
        if current < previous:
            return False
        elif previous == current:
            has_adj_duplicate = True

    return has_adj_duplicate


def match_rules2(val):
    digits = list(map(int, str(val)))
    digit_count = {}
    digit_count[digits[0]] = 1

    for index in range(1, len(digits)):
        current = digits[index]
        previous = digits[index - 1]
        if current < previous:
            return False
        elif previous == current:
            digit_count[current] += 1
        else:
            digit_count[current] = 1

    return 2 in digit_count.values()


def part1(file):
    start, end = list(map(lambda x: int(x, 10), file.read().split('-')))
    count = sum(1 for i in range(start, end+1) if match_rules1(i))
    print(f"Answer: {count}")


def part2(file):
    start, end = list(map(lambda x: int(x, 10), file.read().split('-')))
    count = sum(1 for i in range(start, end+1) if match_rules2(i))
    print(f"Answer: {count}")


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
