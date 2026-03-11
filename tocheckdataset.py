import os

real = sum(len(files) for _, _, files in os.walk("data/real"))
fake = sum(len(files) for _, _, files in os.walk("data/fake"))

print("Real images:", real)
print("Fake images:", fake)
