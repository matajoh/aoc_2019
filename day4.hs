import Test.HUnit
import Data.Maybe
import Control.Parallel.Strategies

data DigitCount = DigitCount { digit :: Char,
                             count :: Int } deriving (Eq, Ord, Show)

incrementCount :: DigitCount -> DigitCount
incrementCount (DigitCount digit count) = DigitCount digit (count+1)

checkNumber' :: String -> DigitCount -> [DigitCount] -> Maybe [DigitCount]
checkNumber' digits count counts
    | null digits = Just (reverse (count:counts))
    | digit count > head digits = Nothing
    | digit count == head digits = checkNumber' (tail digits) (incrementCount count) counts
    | otherwise = checkNumber' (tail digits) (DigitCount (head digits) 1) (count:counts)

validateCount :: [DigitCount] -> Bool
validateCount counts
    | null counts = False
    | count (head counts) > 1 = True
    | otherwise = validateCount (tail counts)

checkNumber :: Int -> Bool
checkNumber number = do
    let counts = checkNumber' (show number) (DigitCount '0' 0) []
    isJust counts && validateCount (fromJust counts)

validateCountExact :: [DigitCount] -> Bool
validateCountExact counts
    | null counts = False
    | count (head counts) == 2 = True
    | otherwise = validateCountExact (tail counts)

checkNumberExact :: Int -> Bool
checkNumberExact number = do
    let counts = checkNumber' (show number) (DigitCount '0' 0) []
    isJust counts && validateCountExact (fromJust counts)

countInRange :: Int -> Int -> (Int -> Bool) -> Int
countInRange start end check = length (filter (==True) (parMap rseq check [start..end]))

makeTest :: (String, Int -> Bool, Int, Bool) -> Test                                                                                     
makeTest (name, func, number, expected) =                                                                                                  
            name ~: expected ~=? func number

testCheckNumber = map makeTest [
    ("checkNumber0", checkNumber, 111111, True),
    ("checkNumber1", checkNumber, 223450, False),
    ("checkNumber2", checkNumber, 123789, False)]

testCheckNumberExact = map makeTest [
    ("checkNumberExact0", checkNumberExact, 112233, True),
    ("checkNumberExact1", checkNumberExact, 123444, False),
    ("checkNumberExact2", checkNumberExact, 111122, True)]

tests = test (testCheckNumber ++ testCheckNumberExact)

main = do
    let start = 178416
    let end = 676461
    
    putStrLn ("Part 1: " ++ show (countInRange start end checkNumber))
    putStrLn ("Part 2: " ++ show (countInRange start end checkNumberExact))