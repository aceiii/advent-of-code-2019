#!/usr/bin/env python3

import sys


def part1(file):
    fuel = map(lambda x: (int(x, 10) // 3) - 2, file.readlines())
    print(sum(fuel))


def fuel_cost(mass):
    fuel = (mass // 3) - 2
    if fuel <= 0:
        return 0
    return fuel + fuel_cost(fuel)


def part2(file):
    fuel = map(lambda x: fuel_cost(int(x, 10)), file.readlines())
    print(sum(fuel))


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
