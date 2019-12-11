import Data.Maybe
import qualified Data.Map as Map
import Test.HUnit
import Debug.Trace
import System.IO
import System.FilePath

data Body = Body { 
    name :: String,
    satellites :: [Body]
} deriving Show

-- TODO use map, as it doesn't seem possible to build a tree?

mapJust :: (Body -> Maybe a) -> [Body] -> [Maybe a]
mapJust func bodies = filter isJust (map func bodies)

countOrbits :: Int -> Body -> Int
countOrbits depth (Body name satellites)
    | null satellites = depth
    | otherwise = depth + sum (map (countOrbits (depth + 1)) satellites)
    
distanceTo :: String -> Body -> Maybe Int
distanceTo target (Body name satellites)
    | name == target = Just 0
    | null satellites = Nothing
    | otherwise = do
        let distances = mapJust (distanceTo target) satellites
        if null distances then
            Nothing
        else
            Just(+1) <*> minimum distances

minJust :: [Maybe Int] -> Int
minJust values = fromJust (minimum values)

-- TODO this is horrible. A much better solution would do something like:
-- 1. find the path down the tree to each thing, record distance to node
-- 2. for all elements in both lists, find the min sum

findShortestTransfer :: String -> String -> Body -> Maybe Int
findShortestTransfer name0 name1 (Body name satellites)
    | null satellites = Nothing
    | otherwise = do
        let path_distance = filter (/=Nothing) (map (findShortestTransfer name0 name1) satellites)

        if not (null path_distance) then
            minimum path_distance
        else do
            let distances0 = mapJust (distanceTo name0) satellites
            let distances1 = mapJust (distanceTo name1) satellites

            if null distances0 || null distances1 then
                Nothing
            else 
                Just (minJust distances0 + minJust distances1)

prep :: Char -> Char
prep char
    | char == ')' = ' '
    | otherwise = char

splitOrbit :: String -> Map.Map String [String]
splitOrbit orbit = do
    let name:satellites = words (map prep orbit)
    Map.fromList [(name, satellites)]

parseOrbits :: [String] -> Map.Map String [String]
parseOrbits orbits = foldl (Map.unionWith (++)) Map.empty (map splitOrbit orbits)

buildTree :: Map.Map String [String] -> String -> Body
buildTree orbitMap name 
    | Map.member name orbitMap = Body name (map (buildTree orbitMap) (fromJust (Map.lookup name orbitMap)))
    | otherwise = Body name []

parseCOM :: [String] -> Body
parseCOM orbits = buildTree (parseOrbits orbits) "COM"

testOrbits0 = [
    "COM)B",
    "B)C",
    "C)D",
    "D)E",
    "E)F",
    "B)G",
    "G)H",
    "D)I",
    "E)J",
    "J)K",
    "K)L"]

testOrbits1 = [
    "COM)B",
    "B)C",
    "C)D",
    "D)E",
    "E)F",
    "B)G",
    "G)H",
    "D)I",
    "E)J",
    "J)K",
    "K)L",
    "K)YOU",
    "I)SAN"]

tests = test [
    "testCountOrbits" ~: 42 ~=? countOrbits 0 (parseCOM testOrbits0),
    "testFindShortestTransfer" ~: 4 ~=? fromJust (findShortestTransfer "YOU" "SAN" (parseCOM testOrbits1))]

main = do
    let path = ".." ++ [pathSeparator] ++ "inputs" ++ [pathSeparator] ++ "day6.txt"
    contents <- readFile path
    let orbits = lines contents
        com = parseCOM orbits

    putStrLn ("Part 1: " ++ show (countOrbits 0 com))

    putStrLn ("Part 2: " ++ show (fromJust (findShortestTransfer "YOU" "SAN" com)))
