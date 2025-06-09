import random as r
x=(input("Roll the dice y/n: ")).lower()
if x=='y':
    dice1=(r.randint(1,6))
    dice2=(r.randint(1,6))
    print(f"Dice 1: {dice1}, Dice 2: {dice2}")
elif x=='n':
    print ("Thank you ")
else:
    print("Invalid input")      
    