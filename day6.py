#!/usr/bin/env python3

import sys
from collections import deque

class OrbitNode(object):
    def __init__(self, name):
        self._name = name
        self._moons = set()

    def __repr__(self):
        moons = ','.join(moon.name() for moon in self.moons())
        return f"{self._name} ) {moons}"

    def name(self):
        return self._name

    def attach(self, node):
        self._moons.add(node)

    def count(self):
        return len(self._moons)

    def moons(self):
        return self._moons


class TotalOrbitCounter(object):
    def __init__(self, node):
        self._node = node

    def count(self):
        total = 0
        queue = deque()
        queue.append((self._node, 0))

        while queue:
            node, count = queue.pop()
            for moon in node.moons():
                queue.append((moon, count + 1))
            total += count

        return total


class OrbitMap(object):
    def __init__(self, edges):
        self._objects = {}
        self._objects['COM'] = OrbitNode('COM')
        for planet, moon in edges:
            if planet not in self._objects:
                self._objects[planet] = OrbitNode(planet)
            if moon not in self._objects:
                self._objects[moon] = OrbitNode(moon)
            self._objects[planet].attach(self._objects[moon])

    def node(self, name):
        return self._objects[name]

    def com(self):
        return self.node('COM')

    def totalOrbits(self):
        moon = list(self.com().moons())[0]
        counter = TotalOrbitCounter(self.com())
        return counter.count()


def orbit_parents(node, target):
    queue = deque([(node, [])])
    while queue:
        planet, path = queue.pop()
        if planet.name() == target:
            return path
        for moon in planet.moons():
            queue.append((moon, path + [planet.name()]))
    return []


def part1(file):
    lines = list(map(lambda x: x.strip().split(')'), file.readlines()))
    orbit_map = OrbitMap(lines)
    print(f"Answer: {orbit_map.totalOrbits()}")


def part2(file):
    lines = list(map(lambda x: x.strip().split(')'), file.readlines()))
    orbit_map = OrbitMap(lines)
    you = deque(orbit_parents(orbit_map.com(), 'YOU'))
    san = deque(orbit_parents(orbit_map.com(), 'SAN'))
    while you and san and you[0] == san[0]:
        you.popleft()
        san.popleft()
    transfers = len(you) + len(san)
    print(f"Answer: {transfers}")


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
