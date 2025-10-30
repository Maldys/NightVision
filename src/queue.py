
#fronta
class Queue:
    def __init__(self):
        self.queue = []

    def __str__(self):
        out = ""
        for element in self.queue:
            out = out + str(element) + ", "
        return out

    def add(self, element):
        self.queue.append(element)
    
    def get_first(self):
        if not self.queue:
            #print("queue is empty")
            return
        return_element = self.queue.pop(0)
        return return_element
