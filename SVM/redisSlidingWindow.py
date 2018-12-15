
import redis

class SlidingWindow(object):
    
    #Create Redis sliding window object, default size 100
    def __init__(self, debugOn = True, queueSize = 100, host="localhost", port=6379, newsQueueName="news"):
        self.db = redis.Redis(host=host, port=port)
        self.newsQueueSize = queueSize
        self.newsQueueName = newsQueueName
        if debugOn == 1:
            debugOn = True
        self.debugOn = debugOn
            
    
    def endRedis(self):
        self.db.connection_pool.disconnect()
        
    def put(self, key, value):
        if not isinstance(value,dict):
            if self.debugOn:print ("Value needs to be a dictionary " + key)
            return False
        if not isinstance(key,str):
            if self.debugOn:print ("Key needs to be a string " + key)
            return False
        self.db.hmset(key, value)
        return True
    
    def get(self, key):
        if not isinstance(key,str):
            if self.debugOn:print ("Key needs to be a string " + key)
            return False
        elif not self.db.exists(key):
            if self.debugOn:print ("Key doesnt exist " + key)
            return False
        
        val = self.db.hgetall(key)
        return val
    
    def delete(self, key):
        if key == self.newsQueueName:
            if self.debugOn:print ("Call freeQueue() function instead")
            return False
        
        if not self.db.exists(key):
            if self.debugOn:print ("Key doesnt exist " + key)
            return False
        
        self.db.delete(key)
        return True
    
    def deleteAll(self):
        for key in self.db.keys():
            # delete the key
            self.db.delete(key)
                      
    def checkIfKeyExists(self, key):
        if self.db.exists(key):
            return True
        else:
            return False
        
    ######################Queue implementation starts here###################
    
    
    def getLengthOfQueue(self):
        return self.db.llen(self.newsQueueName)
    
    #Check if Queue full
    def isQueueFull(self):
        if self.getLengthOfQueue() <= self.newsQueueSize:
            return False
        return True
    
    #pushed value from end of queue (Pops oldest news)
    def popQ(self):
        val = self.db.rpop(self.newsQueueName)
        return val 
    
    #pushed value to top of news queue
    #Returns True if queue is over the capacity, else false
    def pushQ(self, value): 
        #Dont push if object corresponding to key being pushed into queue exists
        if self.checkIfKeyExists(value):
            if self.debugOn:print ("This key already exists")
            return False
        self.db.lpush(self.newsQueueName,value)
        if self.isQueueFull():
            return 2
        return True
    
    #Get values from start to end positions of newws queue
    def getFromQueue(self, start, end):
        val = self.db.lrange(self.newsQueueName, start, end)
        return val
    
    #Get entire news queue content
    def getQ(self):
        return self.getFromQueue(0,self.newsQueueSize-1)
    
    def freeQueue(self):
        keys = self.getQ()
        for key in keys:
            key = key.decode("utf-8")
            self.delete(key)
        self.db.delete(self.newsQueueName)
    
    ################Sliding window key-value object storage implementation##################
    
    #Insert into sliding window
    def insertObject(self, key, value):
        key = str(key)
        if self.debugOn:print("Pushing key ", key)
        
        if self.checkIfKeyExists(key):
            if self.debugOn:print ("Key already exists")
            return False
        
        if key == self.newsQueueName:
            if self.debugOn:print ("Cant use this key")
            return False
        
        isQueueFull = self.pushQ(key)
        if not isQueueFull:
            if self.debugOn:print ("Something went wrong")
            return False
        
        if isQueueFull == 2:
            keyToDelete = self.popQ()
            self.delete(keyToDelete)
            
        self.put(key, value)
        return True
    
    #Get sliding windows content
    def getObjects(self):
        keys = self.getQ()
        objects = []
        for key in keys:
            key = key.decode("utf-8") 
            value = self.get(key)
            dct = {key:value}
            objects.append(dct)
        
        return objects
            
        