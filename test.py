class Person:
    def __init__(self, name, age, height, weight, food):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.food = food
        
    def greet(self):
        print(f"Hello, my name is {self.name}, I am {self.age} years old, I am {self.height} cm tall, and I weigh {self.weight} kg.")
        print(f"My favorite food is {self.food}.")
        
    def celebrate_birthday(self):
        self.age += 1
        print(f"Happy Birthday to me! I am now {self.age} years old.")
        
person1 = Person("Chauncey", 17, 188, 67, "pizza")

person1.greet()
person1.celebrate_birthday()