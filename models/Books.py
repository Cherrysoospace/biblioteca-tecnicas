class Book:
    def __init__(self, ISBNCode, title, author, weight, price, isBorrowed):
        self.__ISBNCode = ISBNCode #String
        self.__title = title #String
        self.__author = author #String
        self.__weight = weight #float
        self.__price = price #int
        self.__isBorrowed = isBorrowed #Boolean

    #Getters Ejemplos
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
    