module Intcode  
( runProgram
) where  

import qualified Data.Map as Map
import Data.Maybe
import Test.HUnit


memToList :: Map.Map Integer Integer -> [Integer] -> [Integer]
memToList memory keys = [v | k <- keys, let v = fromJust (Map.lookup k memory)]

mathOp' :: Integer -> Integer -> Integer -> Integer
mathOp' code lhs rhs
    | code == 1 = lhs + rhs
    | code == 2 = lhs * rhs
    | otherwise = error ("Invalid math op")

mathOp :: Integer -> Map.Map Integer Integer -> Map.Map Integer Integer
mathOp counter memory = do
    let code:lhs:rhs:output:_ = memToList memory [counter..(counter + 3)]
    let lhs' = fromJust (Map.lookup lhs memory)
    let rhs' = fromJust (Map.lookup rhs memory)
    let value = mathOp' code lhs' rhs'
    Map.insert output value memory

runProgram' :: Map.Map Integer Integer -> Integer -> [Integer]
runProgram' memory counter
    | code == 99 = do
        let max_index = toInteger (length memory - 1)
        [v | k <- [0..max_index], let v = fromJust (Map.lookup k memory)]
    | elem code [1, 2] = runProgram' (mathOp counter memory) (counter + 4)
    | otherwise = error "Invalid op code"
    where code = fromJust (Map.lookup counter memory)

runProgram :: [Integer] -> [Integer]
runProgram program = do
    let max_index = toInteger (length program - 1)
    let memory = Map.fromList (zip [0..max_index] program)
    runProgram' memory 0


makeTest :: ([Integer], [Integer]) -> Test                                                                                     
makeTest (program, memory) =                                                                                             
            ("runProgram " ++ show program) ~: memory ~=? runProgram program

tests = test (map makeTest [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50])])
