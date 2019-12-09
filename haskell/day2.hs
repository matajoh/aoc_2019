import Intcode
import Control.Applicative
import System.IO
import System.FilePath
import Debug.Trace

makeTuples = liftA2 (,)

testNounVerb :: [Int] -> (Int, Int) -> (Int, (Int, Int))
testNounVerb program nounVerb = do
    let (noun, verb) = nounVerb
    let a:_:_:program' = program
    let nvProgram = a:noun:verb:program'
    let (Computer memory _ _ _) = runProgram nvProgram
    let result = head (dump memory)
    (result, nounVerb)

part1 :: [Int] -> Int
part1 program = do
    let (result, _) = testNounVerb program (12, 2)
    result

part2 :: [Int] -> Int -> Int
part2 program target = do
    let nounVerbs = makeTuples [0..99] [0..99]
    let results = map (testNounVerb program) nounVerbs
    let (_, (noun, verb)):_ = filter (\(result, _) -> result == target) results
    noun*100 + verb

prep :: Char -> Char
prep char
    | char == ',' = ' '
    | otherwise = char


main = do
    let path = ".." ++ [pathSeparator] ++ "inputs" ++ [pathSeparator] ++ "day2.txt"
    contents <- readFile path
    let values = words (map prep contents)
        program = map read values :: [Int]

    putStrLn ("part 1: " ++ show (part1 program))
    putStrLn ("part 2: " ++ show (part2 program 19690720))
