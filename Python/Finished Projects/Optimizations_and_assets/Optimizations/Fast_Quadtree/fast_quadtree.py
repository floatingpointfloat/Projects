#Optimized quadtree utilizing arrays for faster computation and less overhead in comparison to the class-based quadtree implementation

class QuadTree:
    def __init__(self, x, y, width, height, max_nodes=100000, capacity=4, max_depth=15):
        self.x = [0] * max_nodes
        self.y = [0] * max_nodes
        self.width = [0] * max_nodes
        self.height = [0] * max_nodes
        self.mid_x = [0] * max_nodes
        self.mid_y = [0] * max_nodes

        self.depth = [0] * max_nodes
        self.node_count = 0
        self.capacity = capacity
        self.max_depth = max_depth

        #Root node
        self.x[0] = x
        self.y[0] = y
        self.width[0] = width
        self.height[0] = height
        self.mid_x[0] = x + width / 2
        self.mid_y[0] = y + height / 2
        
    def return_rectangles(self):
        rectangles = []
        for i in range(self.node_count):
            rectangles.append((self.x[i], self.y[i], self.width[i], self.height[i]))
            return rectangles

    