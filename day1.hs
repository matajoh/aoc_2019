import           Test.HUnit
import           System.FilePath

fuelFor :: Integer -> Integer
fuelFor mass = do
    let fuel = fromInteger mass / 3.0
    floor fuel - 2

totalFuelFor :: Integer -> Integer
totalFuelFor mass
    | mass <= 0 = 0
    | otherwise = do
        let fuel = max 0 (fuelFor mass)
        fuel + totalFuelFor fuel


makeTest :: (String, Integer -> Integer, Integer, Integer) -> Test
makeTest (name, func, mass, fuel) =
    (name ++ " " ++ show mass) ~: fuel ~=? func mass


fuelForTests = map
    makeTest
    [ ("fuelFor", fuelFor, 12    , 2)
    , ("fuelFor", fuelFor, 14    , 2)
    , ("fuelFor", fuelFor, 1969  , 654)
    , ("fuelFor", fuelFor, 100756, 33583)
    ]


totalFuelForTests = map
    makeTest
    [ ("totalFuelFor", totalFuelFor, 14    , 2)
    , ("totalFuelFor", totalFuelFor, 1969  , 966)
    , ("totalFuelFor", totalFuelFor, 100756, 50346)
    ]


tests = test (fuelForTests ++ totalFuelForTests)

main = do
    let input_path = "inputs" ++ [pathSeparator] ++ "day1.txt"
    contents <- readFile input_path
    let values = lines contents
        mass   = map read values :: [Integer]

    let fuel = sum (map fuelFor mass)
    putStrLn ("part 1: " ++ show fuel)

    let totalFuel = sum (map totalFuelFor mass)
    putStrLn ("part 2: " ++ show totalFuel)
