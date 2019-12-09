
import Intcode
import System.IO
import System.FilePath

prep :: Char -> Char
prep char
    | char == ',' = ' '
    | otherwise = char

main = do
    let path = "inputs" ++ [pathSeparator] ++ "day5.txt"
    contents <- readFile path
    let values = words (map prep contents)
        program = map read values :: [Int]

    let part1 = runProgramWithInputs program [1]
    let (_, part1Output) = readFromOutput part1
    putStrLn ("Part 1: " ++ show part1Output)

    let part2 = runProgramWithInputs program [5]
    let (_, part2Output) = readFromOutput part2
    putStrLn ("Part 2: " ++ show part2Output)
