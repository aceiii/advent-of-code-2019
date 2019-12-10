#!/usr/bin/env python3

import sys
from math import atan2


def detect_asteroids(asteroids, source):
    sx, sy = source
    angles = set()
    for asteroid in asteroids:
        if asteroid is source:
            continue
        x, y = asteroid
        angles.add(atan2(y - sy, x - sx))
    return len(angles)


def part1(file):
    lines = map(lambda x: x.strip(), file.readlines())

    asteroids = []
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c != '#':
                continue
            asteroids.append((x, y))

    detected = 0
    for asteroid in asteroids:
        detected = max(detected, detect_asteroids(asteroids, asteroid))

    print(f"Answer: {detected}")


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
