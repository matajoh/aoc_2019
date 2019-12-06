data Point = Point { x :: Int,
                     y :: Int} deriving (Eq, Ord, Show)


up :: Point -> Point
up (Point x y) = Point x (y-1)

down :: Point -> Point
down (Point x y) = Point x (y + 1)

left :: Point -> Point
left (Point x y) = Point (x - 1) y

right :: Point -> Point
right (Point x y) = Point (x + 1) y

data Segment = Horizontal Point Point | Vertical Point Point deriving (Eq, Ord, Show)

points :: Segment -> [Point]
points (Horizontal start end)
    | start == end = [start]
    | start < end = start:(points (Horizontal (right start) end))
    | otherwise = start:(points (Horizontal (left start) end))
points (Vertical start end)
    | start == end = [start]
    | start < end = start:(points (Vertical (down start) end))
    | otherwise = start:(points (Vertical (up start) end))

