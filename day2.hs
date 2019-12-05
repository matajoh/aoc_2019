import Intcode

makeTuples :: [Integer] -> [Integer] -> [(Integer, Integer)]
makeTuples i_vals j_vals
    | length(i_vals) == 0 = []
    | otherwise = do
        let i:i_vals' = i_vals
        (map (\j -> (i, j)) j_vals) ++ (makeTuples i_vals' j_vals)

testNounVerb :: [Integer] :: (Integer, Integer) :: Integer :: Maybe (Integer, Integer)
testNounVerb program nounVerb target =
    let noun, verb = nounVerb
    let a:_:_:program' = program
    let nvProgram = a:noun:verb:program'
    head (Intcode.runProgram(nvProgram))
        | 
    if result 



part2 :: [Integer] -> Integer
part2 memory = do
    