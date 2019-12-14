#!/usr/bin/env python3

import sys
from math import ceil
from collections import deque, defaultdict


class NanoFactory(object):
    def __init__(self, reactions):
        self._chemicals = {}
        for output, inputs in reactions:
            chemical, _ = output
            self._chemicals[chemical] = (output, inputs)
            self._chemicals['ORE'] = ((1, 'ORE'), [])

    def chemical(self, name):
        return self._chemicals[name]

    def calculateOre(self, fuel):
        queue = deque()
        queue.append((fuel, 'FUEL'))
        reserves = defaultdict(lambda: 0)
        ore = 0
        while queue:
            required, name = queue.pop()
            if name == 'ORE':
                ore += required
                continue

            if reserves[name] >= required:
                reserves[name] -= required
                continue

            (chemical, count), inputs = self._chemicals[name]
            multiplier = ceil((required - reserves[name]) / count)
            for input_name, input_count in inputs:
                queue.append((multiplier * input_count, input_name))

            reserves[name] += multiplier * count
            queue.append((required, name))

        return ore


def parse_chemical(line):
    head, chemical = line.strip().split(' ')
    count = int(head, 10)
    return (chemical, count)


def parse_reaction(line):
    head, tail = line.strip().split('=>')
    output = parse_chemical(tail)
    inputs = list(map(parse_chemical, head.strip().split(',')))
    return (output, inputs)


def part1(file):
    reactions = list(map(parse_reaction, file.readlines()))
    factory = NanoFactory(reactions)
    ore = factory.calculateOre(1)
    print(f"Answer: {ore}")


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
