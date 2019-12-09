module Intcode  
( Computer,
  Memory,
  toMemory,
  runProgram,
  runProgramWithInputs,
  run,
  step,
  readFromOutput,
  writeToInput,
  needsInput,
  hasOutput,
  isHalted
) where  

import qualified Data.Map as Map
import Data.Maybe
import Test.HUnit
import Debug.Trace


type Memory = Map.Map Int Int

data Computer = Computer {
    memory :: Memory,
    counter :: Int,
    inputs :: [Int],
    outputs :: [Int]
} deriving Show


readFrom :: Memory -> Int -> Int
readFrom memory key = fromJust (Map.lookup key memory)

opcode :: Computer -> Int
opcode (Computer memory counter _ _) = readFrom memory counter

writeTo :: Memory -> Int -> Int -> Memory
writeTo memory key value = Map.insert key value memory

toList :: Memory -> [Int] -> [Int]
toList memory keys = [v | k <- keys, let v = readFrom memory k]

dump :: Memory -> [Int]
dump memory = toList memory [0..(length memory - 1)]

toMemory :: [Int] -> Memory
toMemory values = Map.fromList (zip [0..(length values - 1)] values)

data Operation = Operation {
    code :: Int,
    call :: Computer -> [Int] -> Computer,
    num_params :: Int,
    num_outputs :: Int
}

data ParameterMode = Position | Immediate
           deriving (Eq, Ord, Show, Read, Bounded, Enum)

modes' :: Int -> Int -> [ParameterMode]
modes' opcode num_modes
    | num_modes == 0 = []
    | mod opcode 10 == 1 = Immediate:modes' (div opcode 10) (num_modes - 1)
    | otherwise = Position:modes' (div opcode 10) (num_modes - 1)

modes :: Operation -> Int -> [ParameterMode]
modes (Operation _ _ num_params num_outputs) opcode = do
    let num_modes = num_params + num_outputs
    modes' (div opcode 100) num_modes

params' :: Memory -> [Int] -> [ParameterMode] -> [Int]
params' memory values modes
    | null values = []
    | head modes == Position = readFrom memory (head values):params' memory (tail values) (tail modes)
    | otherwise = head values:params' memory (tail values) (tail modes)

params :: Operation -> Computer -> [Int]
params op computer = do
    let param_modes = modes op (opcode computer)
    let start = counter computer + 1
    let end = start + num_params op - 1
    let values = toList (memory computer) [start..end]
    let outputs = toList (memory computer) [(end + 1)..(end + num_outputs op)]
    let param_values = params' (memory computer) values param_modes
    param_values ++ outputs

execute :: Operation -> Computer -> Computer
execute op computer = call op computer (params op computer)

add :: Computer -> [Int] -> Computer
add (Computer memory counter inputs outputs) params = do
    let lhs:rhs:output:_ = params
    let memory' = writeTo memory output (lhs + rhs)
    Computer memory' (counter + 4) inputs outputs

multiply :: Computer -> [Int] -> Computer
multiply (Computer memory counter inputs outputs) params = do
    let lhs:rhs:output:_ = params
    let memory' = writeTo memory output (lhs * rhs)
    Computer memory' (counter + 4) inputs outputs

input :: Computer -> [Int] -> Computer
input (Computer memory counter inputs outputs) params = do
    let output:_ = params
    let memory' = writeTo memory output (head inputs)
    Computer memory' (counter + 2) (tail inputs) outputs

output :: Computer -> [Int] -> Computer
output (Computer memory counter inputs outputs) params = do
    let value:_ = params
    Computer memory (counter + 2) inputs (value:outputs)

jumpIfTrue :: Computer -> [Int] -> Computer
jumpIfTrue (Computer memory counter inputs outputs) params = do
    let test:value:_ = params
    if test == 0 then
        Computer memory (counter + 3) inputs outputs
    else
        Computer memory value inputs outputs

jumpIfFalse :: Computer -> [Int] -> Computer
jumpIfFalse (Computer memory counter inputs outputs) params = do
    let test:value:_ = params
    if test == 0 then
        Computer memory value inputs outputs
    else
        Computer memory (counter + 3) inputs outputs

lessThan :: Computer -> [Int] -> Computer
lessThan (Computer memory counter inputs outputs) params = do
    let lhs:rhs:output:_ = params
    if lhs < rhs then
        Computer (writeTo memory output 1) (counter + 4) inputs outputs
    else
        Computer (writeTo memory output 0) (counter + 4) inputs outputs
    
equals :: Computer -> [Int] -> Computer
equals (Computer memory counter inputs outputs) params = do
    let lhs:rhs:output:_ = params
    if lhs == rhs then
        Computer (writeTo memory output 1) (counter + 4) inputs outputs
    else
        Computer (writeTo memory output 0) (counter + 4) inputs outputs

       
ops = Map.fromList [
    (1, Operation 1 add 2 1),
    (2, Operation 2 multiply 2 1),
    (3, Operation 3 input 0 1),
    (4, Operation 4 output 1 0),
    (5, Operation 5 jumpIfTrue 2 0),
    (6, Operation 6 jumpIfFalse 2 0),
    (7, Operation 7 lessThan 2 1),
    (8, Operation 8 equals 2 1)]

op :: Int -> Operation
op code = fromJust (Map.lookup code ops)

run :: Computer -> Computer
run computer
    | code == 99 = computer
    | Map.member code ops = do
        let computer' = execute (op code) computer
        run computer'
    | otherwise = error "Invalid op code"
    where code = mod (opcode computer) 100

step :: Computer -> Computer
step computer
    | code == 99 = computer
    | Map.member code ops = execute (op code) computer
    | otherwise = error "Invalid op code"
    where code = mod (opcode computer) 100

writeToInput :: Computer -> Int -> Computer
writeToInput (Computer memory counter inputs outputs) value = Computer memory counter (inputs ++ [value]) outputs

readFromOutput :: Computer -> (Computer, Int)
readFromOutput (Computer memory counter inputs outputs) = (Computer memory counter inputs (tail outputs), head outputs)

isHalted :: Computer -> Bool
isHalted computer = opcode computer == 99

hasOutput :: Computer -> Bool
hasOutput (Computer _ _ _ outputs) = not (null outputs)

needsInput :: Computer -> Bool
needsInput computer = null (inputs computer) && opcode computer == 3

runProgramWithInputs :: [Int] -> [Int] -> Computer
runProgramWithInputs program inputs = do
    let memory = toMemory program
    let computer = Computer memory 0 inputs []
    run computer

runProgram :: [Int] -> Computer
runProgram program = runProgramWithInputs program []

makeTest :: ([Int], [Int]) -> Test                                                                                     
makeTest (program, expected) =                                                                                             
            ("runProgram " ++ show program) ~: expected ~=? dump (memory (runProgram program))

tests = test (map makeTest [
    ([1, 0, 0, 0, 99], [2, 0, 0, 0, 99]),
    ([2, 3, 0, 3, 99], [2, 3, 0, 6, 99]),
    ([2, 4, 4, 5, 99, 0], [2, 4, 4, 5, 99, 9801]),
    ([1, 1, 1, 4, 99, 5, 6, 0, 99], [30, 1, 1, 4, 2, 5, 6, 0, 99]),
    ([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50],
     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]),
    ([1101, 100, -1, 4, 0], [1101, 100, -1, 4, 99])])
