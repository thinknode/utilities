from provider import Provider
from time import sleep

def size(collection):
    return len(collection)

class App(Provider):

    """
    App initialization. Initializes the provider and its socket.

    Important!
    Modify this function with care.
    """
    def __init__(self):
        Provider.__init__(self)

    """
    size_x1
    Gets the size of an item. If the item is an array, returns the length of the array. If the item
    is a map, gets the number of keys in the map. This function is allocated 1 core.
    """
    def size_x1(self, collection, progress, fail):
        return size(collection)

    """
    size_x2
    Gets the size of an item. If the item is an array, returns the length of the array. If the item
    is a map, gets the number of keys in the map. This function is allocated 2 cores.
    """
    def size_x2(self, collection, progress, fail):
        return size(collection)

    """
    size_x4
    Gets the size of an item. If the item is an array, returns the length of the array. If the item
    is a map, gets the number of keys in the map. This function is allocated 4 cores.
    """
    def size_x4(self, collection, progress, fail):
        return size(collection)

    """
    size_x8
    Gets the size of an item. If the item is an array, returns the length of the array. If the item
    is a map, gets the number of keys in the map. This function is allocated 8 cores.
    """
    def size_x8(self, collection, progress, fail):
        return size(collection)

    """
    size_x16
    Gets the size of an item. If the item is an array, returns the length of the array. If the item
    is a map, gets the number of keys in the map. This function is allocated 16 cores.
    """
    def size_x16(self, collection, progress, fail):
        return size(collection)


if __name__ == "__main__":

    app = App()
    app.run()