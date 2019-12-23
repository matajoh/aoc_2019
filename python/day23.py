""" Solution to day 23 """

from collections import deque

from intcode import Computer
from common import asset, Vector


class Network:
    """ Represents a network of Intcode servers """

    def __init__(self, program, num_servers=50):
        self.num_servers = num_servers
        self.computers = [Computer(program) for _ in range(num_servers)]
        self.queues = [deque() for _ in range(num_servers)]
        self.idle = [False]*num_servers
        self.nat = None
        self.reset()

    def _start_server(self, index):
        computer = self.computers[index]
        computer.reset()
        while not computer.needs_input:
            computer.step()

        computer.write(index)
        computer.step()
        self.queues[index].clear()

    def _write_from_queue(self, index):
        computer = self.computers[index]
        queue = self.queues[index]
        if queue:
            while queue:
                vec = queue.popleft()
                computer.write(vec.x)
                computer.write(vec.y)

    def _wait_for_outputs(self, index):
        computer = self.computers[index]
        while not computer.num_outputs:
            if computer.needs_input:
                computer.write(-1)
                return False

            computer.step()

        return True

    def _write_output(self, index):
        computer = self.computers[index]
        while computer.num_outputs < 3:
            computer.step()

        if computer.num_outputs == 3:
            address = computer.read()
            x = computer.read()
            y = computer.read()
            packet = Vector(x, y)
            if address == 255:
                self.nat = packet
            else:
                self.queues[address].append(packet)

    def reset(self):
        """ Reset the state of the network """
        self.nat = None
        for i in range(self.num_servers):
            self._start_server(i)

    def part1(self):
        """ Run the network until the NAT is assigned """
        while self.nat is None:
            for i in range(self.num_servers):
                if self.nat is not None:
                    break

                self._write_from_queue(i)
                if self._wait_for_outputs(i):
                    self._write_output(i)

        return self.nat.y

    def part2(self):
        """ Run the network until the same NAT y value is sent twice """
        last_y = None
        idle_count = 0
        while True:
            for i in range(self.num_servers):
                self._write_from_queue(i)
                if self._wait_for_outputs(i):
                    self._write_output(i)
                    self.idle[i] = False
                else:
                    self.idle[i] = True

            if all(self.idle):
                idle_count += 1
                if idle_count > 1:
                    self.queues[0].append(self.nat)
                    if self.nat.y == last_y:
                        return last_y

                    last_y = self.nat.y
            else:
                idle_count = 0


def _main():
    with open(asset("day23.txt")) as file:
        program = [int(part) for part in file.read().split(',')]

    network = Network(program)
    print("Part 1:", network.part1())

    network.reset()
    print("Part 2:", network.part2())


if __name__ == "__main__":
    _main()
