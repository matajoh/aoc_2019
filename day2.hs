import Intcode
import Control.Applicative
import System.IO
import System.FilePath
import Debug.Trace

makeTuples = liftA2 (,)

testNounVerb :: [Integer] -> (Integer, Integer) -> (Integer, (Integer, Integer))
testNounVerb program nounVerb = do
    let (noun, verb) = nounVerb
    let a:_:_:program' = program
    let nvProgram = a:noun:verb:program'
    let result = head (Intcode.runProgram nvProgram)
    (result, nounVerb)

part1 :: [Integer] -> Integer
part1 program = do
    let (result, _) = testNounVerb program (12, 2)
    result

part2 :: [Integer] -> Integer -> Integer
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
    let path = "inputs" ++ [pathSeparator] ++ "day2.txt"
    contents <- readFile path
    let values = words (map prep contents)
        program = map read values :: [Integer]

    putStrLn ("part 1: " ++ (show (part1 program)))
    putStrLn ("part 2: " ++ (show (part2 program 19690720)))
