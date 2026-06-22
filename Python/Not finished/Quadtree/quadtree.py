#quadtree for usage in other projects

class QuadNode:
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
                 'depth'] #use __slots__ to save memory since we know exactly what attributes we need - just faster and more memory efficient than using a normal class with __dict__
    
    CAPACITY = 4 #max points per node before subdivision
    MAX_DEPTH = 15 #max depth to prevent infinite subdivision
    MIN_SIZE = 1
    
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

        self.depth = depth
        
    def draw_tree(self, rectangles): #just for debugging and visualization purposes - draw the tree structure using pygame or something like that
        rectangles.append((self.x, self.y, self.width, self.height))
        if self.nw is not None:
            self.nw.draw_tree(rectangles)
            self.ne.draw_tree(rectangles)
            self.sw.draw_tree(rectangles)
            self.se.draw_tree(rectangles)
    
    def get_child(self, x, y):
        if x < self.mid_x: #point is in the left half
            if y < self.mid_y: #point is in the top half
                return self.nw
            else: #point is in the bottom half
                return self.sw
        else: #point is in the right half
            if y < self.mid_y: #point is in the top half
                return self.ne
            else: #point is in the bottom half
                return self.se

    def subdivide(self):
        half_width = self.width / 2
        half_height = self.height / 2
        new_depth = self.depth + 1
        
        self.nw = QuadNode(self.x, self.y, half_width, half_height, new_depth)
        self.ne = QuadNode(self.mid_x, self.y, half_width, half_height, new_depth)
        self.sw = QuadNode(self.x, self.mid_y, half_width, half_height, new_depth)
        self.se = QuadNode(self.mid_x, self.mid_y, half_width, half_height, new_depth)

    def intersects(self, x, y): #does the point lie within the bounds of this node?
        return (self.x <= x < self.x + self.width and self.y <= y < self.y + self.height)
        
    def intersects_circle(self, x, y, radius_sq): #does the point lie within the bounds of this node?
        closest_x = max(self.x, min(x, self.x + self.width))
        closest_y = max(self.y, min(y, self.y + self.height))
        
        dist_x = x - closest_x
        dist_y = y - closest_y
        
        return dist_x * dist_x + dist_y * dist_y <= radius_sq
    
    def insert_to_children(self, x, y): #try to insert the point into the children - return True if successful, False if not
        child = self.get_child(x, y)
        return child.insert(x, y)
    
    def insert(self, x, y): #insert a point into the quadtree, return True if successful, False if the point is outside the bounds of this node or if the insertion simply failed for some reason
        if not self.intersects(x, y): #point is outside the bounds of this node
            return False
        
        if self.nw is None: #if this node is a leaf, try to insert the point here
            if len(self.points) < QuadNode.CAPACITY or self.depth >= QuadNode.MAX_DEPTH or self.width <= QuadNode.MIN_SIZE or self.height <= QuadNode.MIN_SIZE: #if there is still capacity or we have reached max depth, insert the point here
                self.points.append((x, y))
                return True
            else: #otherwise, we need to subdivide and redistribute the points
                self.subdivide()
                for px, py in self.points:
                    self.insert_to_children(px, py)
                self.points.clear() #clear the points from this node since they are now stored in the children
                return self.insert_to_children(x, y) #try to insert the new point into the children as well
        else: #if this node is not a leaf, try to insert the point into the children
            return self.insert_to_children(x, y)
    
    def query(self, x, y, search_range, found_points, search_range_sq=None): #search for points within search_range of (x, y) and add them to found_points - maybe for collision or stuff like that
        if search_range_sq is None:
            search_range_sq = search_range * search_range #use squared distance to avoid unnecessary square root calculations
            
        if not self.intersects_circle(x, y, search_range_sq): #if the search range does not intersect with this node, return
            return
            
        for px, py in self.points: #check the points in this node - if they are within the search range, add them to found_points
            dx = px - x
            dy = py - y
            if dx * dx + dy * dy <= search_range_sq:
                found_points.append((px, py))
                
        if self.nw is not None: #if this node has children, check them as well - also loop unrolling for performance since we know there are only 4 children
            self.nw.query(x, y, search_range, found_points, search_range_sq)
            self.ne.query(x, y, search_range, found_points, search_range_sq)
            self.sw.query(x, y, search_range, found_points, search_range_sq)
            self.se.query(x, y, search_range, found_points, search_range_sq)
    
    def clear(self): #clear the quadtree - maybe for resetting or something
        self.points.clear()

        if self.nw is not None: #if this node has children, clear them as well - also loop unrolling for performance since we know there are only 4 children
            self.nw.clear()
            self.ne.clear()
            self.sw.clear()
            self.se.clear()
            self.nw = self.ne = self.sw = self.se = None
        
#wrapperclass
class QuadTree:
    def __init__(self, x, y, width, height):
        self.root = QuadNode(x, y, width, height)
        
    def insert(self, x, y):
        return self.root.insert(x, y)
    
    def query(self, x, y, search_range):
        found_points = []
        search_range_sq = search_range * search_range #use squared distance to avoid unnecessary square root calculations
        self.root.query(x, y, search_range, found_points, search_range_sq)
        return found_points
    
    def clear(self):
        self.root.clear()
        
    def draw_tree(self): #vizualizations and debugging purposes - return a list of rectangles that represent the nodes of the tree
        rectangles = []
        self.root.draw_tree(rectangles)
        return rectangles
