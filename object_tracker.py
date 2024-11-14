import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict

class CentroidTracker:
    def __init__(self, max_disappeared=50):
        # Initialize the next unique object ID along with two ordered dictionaries
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared

    def register(self, centroid):
        # Register a new object with a unique ID and its centroid
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        # Remove an object ID from tracking
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        # Check if the list of input bounding box rectangles is empty
        if len(rects) == 0:
            # Mark existing objects as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        # Initialize an array of input centroids
        input_centroids = np.zeros((len(rects), 2), dtype="int")

        for (i, (start_x, start_y, end_x, end_y)) in enumerate(rects):
            c_x = int((start_x + end_x) / 2.0)
            c_y = int((start_y + end_y) / 2.0)
            input_centroids[i] = (c_x, c_y)

        # If no objects are currently being tracked, register all input centroids
        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])
        else:
            # Get the current object IDs and centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Compute the distance between each pair of object centroids and input centroids
            D = dist.cdist(np.array(object_centroids), input_centroids)

            # Find the smallest value in each row and column
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            # Keep track of matched and unmatched object IDs and input centroids
            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # Compute indices of unmatched rows and columns
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            # Handle disappeared objects
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            # Register new objects
            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects

