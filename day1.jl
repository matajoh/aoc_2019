using Test
using CSV

function fuelFor(mass)
    return convert(Int64, floor(mass/3) - 2)
end

function totalFuelFor(mass)
    fuel = fuelFor(mass)
    if fuel <= 0
        return 0
    end

    return fuel + totalFuelFor(fuel)
end

function test()
    @test fuelFor(12) == 2
    @test fuelFor(14) == 2
    @test fuelFor(1969) == 654
    @test fuelFor(100756) == 33583
    @test totalFuelFor(14) == 2
    @test totalFuelFor(1969) == 966
    @test totalFuelFor(100756) == 50346
end

function part1(mass)
    fuel = sum(map(fuelFor, mass))
    println("part1: $fuel")
end        

function part2(mass)
    totalFuel = sum(map(totalFuelFor, mass))
    println("part2: $totalFuel")
end

test()

data = CSV.read(joinpath("inputs", "day1.txt"), datarow=1)
mass = data[:, 1]
part1(mass)
part2(mass)
