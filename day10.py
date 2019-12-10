#!/usr/bin/env python3

import sys
from math import pi, atan2
from operator import itemgetter
from collections import deque


def detect_asteroids(asteroids, source):
    sx, sy = source
    angles = set()
    for asteroid in asteroids:
        if asteroid is source:
            continue
        x, y = asteroid
        angles.add(atan2(y - sy, x - sx))
    return len(angles)


def asteroid_sort(asteroids, station):
    sx, sy = station
    angles = {}
    for asteroid in asteroids:
        if asteroid is station:
            continue
        x, y = asteroid
        dx, dy = x - sx, y - sy
        angle = atan2(dy, dx) + (pi / 2.0)
        if angle < 0:
            angle = (2 * pi) + angle
        dist = dx * dx + dy * dy
        if angle not in angles:
            angles[angle] = []
        angles[angle].append((dist, (x, y)))

    sorted_asteroids = []
    for key in sorted(angles.keys()):
        sorted_tuples = sorted(angles[key], key=itemgetter(0))
        queue = deque(map(itemgetter(1), sorted_tuples))
        sorted_asteroids.append(queue)

    return sorted_asteroids


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
    lines = map(lambda x: x.strip(), file.readlines())

    asteroids = []
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c != '#':
                continue
            asteroids.append((x, y))

    detections = [(detect_asteroids(asteroids, asteroid), asteroid)
                  for asteroid in asteroids]

    _, station = sorted(detections, key=itemgetter(0), reverse=True)[0]

    sorted_asteroids = asteroid_sort(asteroids, station)
    popped = []
    index = 0
    while True:
        if len(sorted_asteroids[index]):
            popped.append(sorted_asteroids[index].popleft())
        index = (index + 1) % len(sorted_asteroids)
        if len(popped) == 200:
            break
    x, y = popped[-1]
    print(f"Answer: {(x * 100) + y}")


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
