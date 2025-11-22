class Book:
    def __init__(self, id,ISBNCode, title, author, weight, price, stock):
        self.__id = id
        self.__ISBNCode = ISBNCode #String
        self.__title = title #String
        self.__author = author #String
        self.__weight = weight #float
        self.__price = price #int
        self.__stock = stock  # Default stock value
        # maintain compatibility: initialize borrow flag (used elsewhere)
        self.__isBorrowed = False

    #Getters Ejemplos
    def get_id(self):
        return self.__id

    def get_ISBNCode(self):
        return self.__ISBNCode
    
    def get_title(self):
        return self.__title
    
    def get_author(self):
        return self.__author
    
    def get_weight(self):
        return self.__weight
    
    def get_price(self):
        return self.__price
    
    def get_isBorrowed(self):
        return self.__isBorrowed
    
    def get_stock(self):
        return self.__stock

    #Setters Ejemplos
    def set_ISBNCode(self, ISBNCode):
        self.__ISBNCode = ISBNCode
    
    def set_title(self, title):
        self.__title = title
    
    def set_author(self, author):
        self.__author = author
    
    def set_weight(self, weight):
        self.__weight = weight
    
    def set_price(self, price):
        self.__price = price
    
    def set_isBorrowed(self, isBorrowed):
        self.__isBorrowed = isBorrowed
    
    def set_id(self, id):
        self.__id = id
        
    def set_stock(self, stock):
        self.__stock = stock

    def __str__(self):
        return f"Book[ID: {self.__id}, ISBNCode: {self.__ISBNCode}, Title: {self.__title}, Author: {self.__author}, Weight: {self.__weight}, Price: {self.__price}, Stock: {self.__stock}]"
    