#quadtree for usage in other projects

class QuadNodes:
    __slots__ = ['x', 
                 'y', 
                 'width', 
                 'height', 
                 'mid_x', 
                 'mid_y', 
                 'nw', 
                 'ne', 
                 'sw', 
                 'se', 
                 'points', 
                 'capacity', 
                 'max_depth', 
                 'depth'] #use __slots__ to save memory since we know exactly what attributes we need - just faster and more memory efficient than using a normal class with __dict__
    
    def __init__(self, x, y, width, height, depth=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mid_x = x + width / 2
        self.mid_y = y + height / 2
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
        self.points = []  # Store points if this node is a leaf

        self.capacity = 4  # Max points per node before subdivision
        self.max_depth = 15 # Max depth to prevent infinite subdivision
        self.depth = depth

    def subdivide(self):
        half_width = self.width / 2
        half_height = self.height / 2
        new_depth = self.depth + 1
        
        self.nw = QuadNodes(self.x, self.y, half_width, half_height, new_depth)
        self.ne = QuadNodes(self.mid_x, self.y, half_width, half_height, new_depth)
        self.sw = QuadNodes(self.x, self.mid_y, half_width, half_height, new_depth)
        self.se = QuadNodes(self.mid_x, self.mid_y, half_width, half_height, new_depth)

    def intersects(self, x, y): #does the point lie within the bounds of this node?
        return (self.x <= x < self.x + self.width and self.y <= y < self.y + self.height)
        
    def intersects_circle(self, x, y, radius): #does the point lie within the bounds of this node?
        closest_x = max(self.x, min(x, self.x + self.width))
        closest_y = max(self.y, min(y, self.y + self.height))
        
        dist_x = x - closest_x
        dist_y = y - closest_y
        
        return dist_x * dist_x + dist_y * dist_y <= radius * radius
    
    def insert_to_children(self, x, y): #try to insert the point into the children - return True if successful, False if not
        if x < self.mid_x: #point is in the left half
            if y < self.mid_y: #point is in the top half
                return self.nw.insert(x, y)
            else: #point is in the bottom half
                return self.sw.insert(x, y)
        else: #point is in the right half
            if y < self.mid_y: #point is in the top half
                return self.ne.insert(x, y)
            else: #point is in the bottom half
                return self.se.insert(x, y)
    
    def insert(self, x, y): #insert a point into the quadtree, return True if successful, False if the point is outside the bounds of this node or if the insertion simply failed for some reason
        if not self.intersects(x, y): #point is outside the bounds of this node
            return False
        
        if len(self.points) < self.capacity or self.depth >= self.max_depth: #if this node has capacity for more points or we've reached max depth, add the point here
            self.points.append((x, y))
            return True
        
        if self.nw is not None and self.depth < self.max_depth: #if this node is not a leaf and we haven't reached max depth, try to insert into children
            return self.insert_to_children(x, y)
        
        if self.nw is None and self.depth < self.max_depth and len(self.points) >= self.capacity: #if this node is a leaf and we need to subdivide, do so and then try to insert the existing points into the children
            self.subdivide()
            for px, py in self.points:
                self.insert_to_children(px, py)
            self.points.clear() #clear points from this node since they are now in the children
            return self.insert_to_children(x, y) #try to insert the new point into the children as well
            
        return False #if we get here, the insertion failed for some reason - maybe we reached max depth and still have too many points, or something else went wrong - in any case, return False to indicate failure
    
    def query(self, x, y, search_range, found_points): #search for points within search_range of (x, y) and add them to found_points - maybe for collision or stuff like that
        if not self.intersects_circle(x, y, search_range): #if the search range does not intersect with this node, return
            return
        
        for point in self.points: #check points in this node
            if (point[0] - x) ** 2 + (point[1] - y) ** 2 <= search_range ** 2:
                found_points.append(point)
                
        if self.nw is not None: #if this node has children, check them as well - also loop unrolling for performance since we know there are only 4 children
            self.nw.query(x, y, search_range, found_points)
            self.ne.query(x, y, search_range, found_points)
            self.sw.query(x, y, search_range, found_points)
            self.se.query(x, y, search_range, found_points)
    
    def clear(self): #clear the quadtree - maybe for resetting or something
        self.points.clear()
        
        if self.nw:
            self.nw.clear()
            self.ne.clear()
            self.sw.clear()
            self.se.clear()
            self.nw = self.ne = self.sw = self.se = None
        
#wrapperclass
class QuadTree:
    def __init__(self, x, y, width, height):
        self.root = QuadNodes(x, y, width, height)
        
    def insert(self, x, y):
        return self.root.insert(x, y)
    
    def query(self, x, y, search_range):
        found_points = []
        self.root.query(x, y, search_range, found_points)
        return found_points
    
    def clear(self):
        self.root.clear()
