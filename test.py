from dataclasses import dataclass

@dataclass
class Animal:
	name: str
	weight: int

@dataclass
class Whale(Animal):
	fin_type: str

a = Whale('Bob', 100, 'dorsal')


print(dir(__builtins__))
