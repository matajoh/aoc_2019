import Test.HUnit
import System.IO
import System.FilePath
import Data.List

fuelFor :: Integer -> Integer
fuelFor mass = (floor ((fromInteger mass) / 3.0)) - 2

totalFuelFor :: Integer -> Integer
totalFuelFor mass
    | mass <= 0 = 0
    | otherwise = do
        let fuel = max 0 (fuelFor mass)
        fuel + totalFuelFor fuel

tests = test [ "test1" ~: "fuelFor 12" ~: 2 ~=? fuelFor 12,
               "test2" ~: "fuelFor 14" ~: 2 ~=? fuelFor 14,
               "test3" ~: "fuelFor 1969" ~: 654 ~=? fuelFor 1969,
               "test4" ~: "fuelFor 100756" ~: 33583 ~=? fuelFor 100756,
               "test5" ~: "totalFuelFor 14" ~: 2 ~=? totalFuelFor 14,
               "test6" ~: "totalFuelFor 1969" ~: 966 ~=? totalFuelFor 1969,
               "test7" ~: "totalFuelFor 100756" ~: 50346 ~=? totalFuelFor 100756]

parseInt :: String -> Integer
parseInt = read

main = do
    let path = "inputs" ++ [pathSeparator] ++ "day1.txt"
    handle <- openFile path ReadMode
    contents <- hGetContents handle
    let singlewords = words contents
        mass = map parseInt singlewords

    let fuel = sum (map fuelFor mass)
    putStrLn ("part 1: " ++ (show fuel))
    
    let fuel = sum (map totalFuelFor mass)
    putStrLn("part 2: " ++ (show fuel))
    hClose handle
