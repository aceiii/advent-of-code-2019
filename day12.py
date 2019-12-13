#!/usr/bin/env python3

import sys


class MoonSimulator(object):
    def __init__(self, moons):
        self._moons = [(pos[:], (0, 0, 0)) for pos in moons]
        self._x_states = set()
        self._y_states = set()
        self._z_states = set()
        self._states = set()
        self._step_count = 0
        self._stop_x = False
        self._stop_y = False
        self._stop_z = False

    def step(self):
        accel = [(0, 0, 0) for _ in self._moons]
        for i in range(len(self._moons) - 1):
            for j in range(i+1, len(self._moons)):
                pos1, (vx1, vy1, vz1) = self._moons[i]
                pos2, (vx2, vy2, vz2) = self._moons[j]
                px1, py1, pz1 = pos1
                px2, py2, pz2 = pos2
                ax1, ay1, az1 = accel[i]
                ax2, ay2, az2 = accel[j]

                dx1, dx2 = (1, -1) if px1 < px2 else (0, 0) if px1 == px2 else (-1, 1)
                dy1, dy2 = (1, -1) if py1 < py2 else (0, 0) if py1 == py2 else (-1, 1)
                dz1, dz2 = (1, -1) if pz1 < pz2 else (0, 0) if pz1 == pz2 else (-1, 1)

                accel[i] = (ax1 + dx1, ay1 + dy1, az1 + dz1)
                accel[j] = (ax2 + dx2, ay2 + dy2, az2 + dz2)

        for index, moon in enumerate(self._moons):
            (x, y, z), (vx, vy, vz) = moon
            ax, ay, az = accel[index]
            vx, vy, vz = (vx + ax, vy + ay, vz + az)
            vel = (vx, vy, vz)
            pos = (x + vx, y + vy, z + vz)
            self._moons[index] = (pos, vel)

        x_state = tuple(map(lambda x: (x[0][0], x[1][0]), self._moons))
        y_state = tuple(map(lambda x: (x[0][1], x[1][1]), self._moons))
        z_state = tuple(map(lambda x: (x[0][2], x[1][2]), self._moons))

        if not self._stop_x:
            if x_state in self._x_states:
                self._stop_x = True
            else:
                self._x_states.add(x_state)

        if not self._stop_y:
            if y_state in self._y_states:
                self._stop_y = True
            else:
                self._y_states.add(y_state)

        if not self._stop_z:
            if z_state in self._z_states:
                self._stop_z = True
            else:
                self._z_states.add(z_state)

        self._step_count += 1

    def energy(self):
        total = 0
        for moon in self._moons:
            pos, vel = moon
            pot = sum(map(abs, pos))
            kin = sum(map(abs, vel))
            total += pot * kin
        return total

    def loopTime(self):
        xlen = len(self._x_states)
        ylen = len(self._y_states)
        zlen = len(self._z_states)

        x, y, z = sorted([xlen, ylen, zlen])

        val = z * y
        while True:
            if val % x == 0:
                return val
                break
            val += z * y

    def runUntilLoop(self):
        while True:
            if self._stop_x and self._stop_y and self._stop_z:
                break
            self.step()


def parse_moons(lines):
    moons = []
    for line in lines:
        parts = map(str.strip, line.strip()[1:-1].split(','))
        x, y, z = map(lambda p: int(p[2:], 10), parts)
        moons.append((x, y, z))
    return moons


def part1(file):
    lines = file.readlines()
    moons = MoonSimulator(parse_moons(lines))
    n = 1000
    for _ in range(n):
        moons.step()
    energy = moons.energy()
    print(f"Answer: {energy}")


def part2(file):
    lines = file.readlines()
    moons = MoonSimulator(parse_moons(lines))
    moons.runUntilLoop()
    loop = moons.loopTime()
    print(f"Answer: {loop}")


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
