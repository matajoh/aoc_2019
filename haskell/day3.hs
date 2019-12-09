import qualified Data.Set as Set
import Data.Foldable
import System.IO
import System.FilePath
import Debug.Trace
import Test.HUnit

data Point = Point { x :: Integer,
                     y :: Integer} deriving (Eq, Ord, Show)


up :: Integer -> Point -> Point
up distance (Point x y) = Point x (y-distance)

down :: Integer -> Point -> Point
down distance (Point x y) = Point x (y + distance)

left :: Integer -> Point -> Point
left distance (Point x y) = Point (x - distance) y

right :: Integer -> Point -> Point
right distance (Point x y) = Point (x + distance) y

data Segment = Horizontal {start :: Point, end :: Point } 
             | Vertical {start :: Point, end :: Point}
             | Origin {end :: Point}
             deriving (Eq, Ord, Show)

type Wire = [Segment]

points :: Segment -> [Point]
points (Horizontal start end)
    | start == end = [start]
    | start < end = start:points (Horizontal (right 1 start) end)
    | otherwise = start:points (Horizontal (left 1 start) end)
points (Vertical start end)
    | start == end = [start]
    | start < end = start:points (Vertical (down 1 start) end)
    | otherwise = start:points (Vertical (up 1 start) end)
points (Origin end) = [end]

within :: Integer -> Integer -> Integer -> Bool
within value start end
    | start > end = within value end start
    | otherwise = start <= value && value <= end


contains :: Point -> Segment -> Bool
contains (Point x y) (Horizontal (Point x0 y0) (Point x1 y1)) = y == y0 && within x x0 x1
contains (Point x y) (Vertical (Point x0 y0) (Point x1 y1)) = x == x0 && within y y0 y1
contains (Point x y) (Origin (Point x1 y1)) = x == x1 && y == y1


stepsTo :: Point -> Segment -> Integer
stepsTo (Point x _) (Horizontal (Point x0 _) _) = abs (x - x0)
stepsTo (Point _ y) (Vertical (Point _ y0) _) = abs (y - y0)
stepsTo point (Origin end) = 0

steps :: Segment -> Integer
steps (Horizontal (Point x0 _) (Point x1 _)) = abs (x1 - x0)
steps (Vertical (Point _ y0) (Point _ y1)) = abs (y1 - y0)
steps (Origin _) = 0

prep :: Char -> Char
prep char
    | char == ',' = ' '
    | otherwise = char


makeSegment :: Char -> Point -> String -> Segment
makeSegment dir start distance
    | dir == 'U' = Vertical start (up (read distance :: Integer) start)
    | dir == 'R' = Horizontal start (right (read distance ::Integer) start)
    | dir == 'D' = Vertical start (down (read distance :: Integer) start)
    | dir == 'L' = Horizontal start (left (read distance :: Integer) start)
    | otherwise = error "Invalid direction"


followDirections :: [String] -> Wire -> Wire
followDirections directions segments
    |   null directions = reverse segments
    | otherwise = do
        let start = end (head segments)
        let dir:distance = head directions
        let segment = makeSegment dir start distance
        followDirections (tail directions) (segment:segments)

readWire :: String -> Wire
readWire directions = do
    let directions' = words (map prep directions)
    let segments = [Origin (Point 0 0)]
    followDirections directions' segments

manhattan :: Point -> Integer
manhattan (Point x y) = abs x + abs y

comparePoints :: (Point -> Integer) -> Point -> Point -> Ordering
comparePoints distance lhs rhs = compare (distance lhs) (distance rhs)

findIntersections :: Wire -> Wire -> [Point]
findIntersections wire0 wire1 = do
    let set0 = Set.fromList (concatMap points wire0)
    let set1 = Set.fromList (concatMap points wire1)
    let intersections = Set.delete (Point 0 0) (Set.intersection set0 set1)
    Set.toList intersections

minDistIntersection :: Wire -> Wire -> Integer
minDistIntersection wire0 wire1 = do
    let intersections = findIntersections wire0 wire1
    let minimum = minimumBy (comparePoints manhattan) intersections
    manhattan minimum

totalStepsTo :: Wire -> Point -> Integer
totalStepsTo wire point = do
    let segment:segments = wire
    if contains point segment then
        stepsTo point segment
    else
        steps segment + totalStepsTo segments point

combinedStepsTo :: Wire -> Wire -> Point -> Integer
combinedStepsTo wire0 wire1 point = totalStepsTo wire0 point + totalStepsTo wire1 point

minStepsIntersection :: Wire -> Wire -> Integer
minStepsIntersection wire0 wire1 = do
    let intersections = findIntersections wire0 wire1
    let minimum = minimumBy (comparePoints (combinedStepsTo wire0 wire1)) intersections
    combinedStepsTo wire0 wire1 minimum

makeTest :: (String, Wire -> Wire -> Integer, String, String, Integer) -> Test                                                                                     
makeTest (name, func, dirs0, dirs1, expected) =                                                                                                  
            name ~: expected ~=? func (readWire dirs0) (readWire dirs1)

minDistTests = map makeTest [
    ("testMinDist0", minDistIntersection, "R8,U5,L5,D3", "U7,R6,D4,L4", 6),
    ("testMinDist1", minDistIntersection, "R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", 159),
    ("testMinDist2", minDistIntersection, "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
     "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", 135)]

minStepsTests = map makeTest [
    ("testMinSteps0", minStepsIntersection, "R8,U5,L5,D3", "U7,R6,D4,L4", 30),
    ("testMinSteps1", minStepsIntersection, "R75,D30,R83,U83,L12,D49,R71,U7,L72", "U62,R66,U55,R34,D71,R55,D58,R83", 610),
    ("testMinSteps2", minStepsIntersection, "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51",
     "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7", 410)]

tests = test (minDistTests ++ minStepsTests)

main = do
    let path = ".." ++ [pathSeparator] ++ "inputs" ++ [pathSeparator] ++ "day3.txt"
    contents <- readFile path
    let wire0:wire1:_ = map readWire (lines contents)

    let minDist = minDistIntersection wire0 wire1
    putStrLn ("Part 1: " ++ show minDist)
    
    let minSteps = minStepsIntersection wire0 wire1
    putStrLn ("Part 2: " ++ show minSteps)
