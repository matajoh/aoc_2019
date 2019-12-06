data Point = Point { x :: Int,
                     y :: Int} deriving (Eq, Ord, Show)


up :: Integer -> Point -> Point
up distance (Point x y) = Point x (y-distance)

down :: Integer -> Point -> Point
down distance (Point x y) = Point x (y + distance)

left :: Integer -> Point -> Point
left (Point x y) = Point (x - distance) y

right :: Integer -> Point -> Point
right (Point x y) = Point (x + distance) y

data Segment = Horizontal Point Point | Vertical Point Point deriving (Eq, Ord, Show)

points :: Segment -> [Point]
points (Horizontal start end)
    | start == end = [start]
    | start < end = start:(points (Horizontal (right 1 start) end))
    | otherwise = start:(points (Horizontal (left 1 start) end))
points (Vertical start end)
    | start == end = [start]
    | start < end = start:(points (Vertical (down 1 start) end))
    | otherwise = start:(points (Vertical (up 1 start) end))


prep :: Char -> Char
prep char
    | char == ',' = ' '
    | otherwise = char


makeSegment :: Char -> Point -> Segment
makeSegment dir start
    | dir == 'U' = Vertical start start.up(read distance :: Integer)
    | dir == 'R' = Horizontal start start.right(read distance ::Integer)
    | dir == 'D' = Vertical start start.down(read distance :: Integer)
    | dir == 'L' = Horizontal start start.left(read distance :: Integer)
    | otherwise = error("Invalid direction")


followDirections :: [String] -> [Segment] -> [Segment]
followDirections directions segments
    | length directions == 0 = segments
    | otherwise = do
        let (Segment _ start):_ = segments
        let direction:directions' = directions
        let dir:distance = direction
        let segment = makeSegment dir start
        followDirections (segments ++ segment) directions'

readWire :: String -> [Segment]
readWire directions = followDirections (words (map prep directions) [])
