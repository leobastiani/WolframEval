# Eval equation with Sublime Text 3

With Sublime Text 3 and WolframAlpha you can now resolve equations easily.


### Installation

Add this repository using Sublime Package Control.


### Usage

Use the command palette and type WolframEval with selected equation.


### Commands

| Equation                       | Result                                                       |
|--------------------------------|--------------------------------------------------------------|
| x=pi+1                         | {x = 1 + Pi, x = 4.14159}                                    |
| pi+1                           | 4.141592653589793238462643383279502884197169399375105820974  |
| pi                             | 3.141592653589793238462643383279502884197169399375105820974  |
| 4*x+3 = 8                      | {x = 5/4, {1.25}}                                            |
| 4*y+x+z+3=8, x                 | x = 5 - 4*y - z                                              |
| var1 + var2 = 5, var1-var2 = 6 | {{var1 = 11/2, var2 = -1/2}}                                 |
| x^2+y^2=1, (x-2)^2+(y-1)^2=4   | {x = 0, y = 1}, {x = 4/5, y = -3/5}                          |
| x+y+z=20, x+y-z=30, x-y+z=40   | {{z = -5, x = 35, y = -10}}                                  |
| x+y+z=20, x+y-z=30, y          | y = 25 - x && z = -5                                         |
| z=1+pi                         | {z = 1 + Pi, z = 4.14159}                                    |
| z=1+e                          | {z = 1 + E, z = 3.71828}                                     |
| z=1+e                          | {z = 1 + E, z = 3.71828}                                     |
| (x - 2)^2 + (y - 1)^2 = 4, x   | x = 2 - Sqrt[3 + 2*y - y^2] \|\| x = 2 + Sqrt[3 + 2*y - y^2] |
