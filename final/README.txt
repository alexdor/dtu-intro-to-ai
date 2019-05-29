
README

Install Dependencies
In order to set up the dependencies of the program, the user has to do the following steps:
  1.  Unzip the folder that includes the program.
  2.  Install python3.7 ( https://www.python.org/downloads/ ) 
  3.  Open a terminal and navigate to the folder of the program.
  4.  Install the dependencies of the program by running `pip3 install -r requirments.txt`.


Execute the program
  1.  In order to execute the program the user needs to open a terminal and navigate to the folder of the program.
  2.  Execute the program by running `python3 kb.py` (Note: the users wants to see the truth table and other information used for debugging the program, he/she can run the program with this command `python3 kb.py --debug`)
  3.  Then the user may input their knowledge base.

The following symbols are used to represent the logic symbols used in the statements:
not = !
or = |
and = &
implies = ->
biconditional = <->

The user can also use comma (,) to separate clauses and use parentheses to group clauses together.

When the prompt “Enter a new clause:” appears, the user can enter a new statement using letters and the symbols above.  The agent will evaluate if the knowledge base is satisfiable and it will print the output of this evaluation.  If it isn’t, the agent will perform partial meet contraction to remove the conflicting clause from the knowledge base.

Finally the user can exit the program by typing on of the following words:
  •  quit
  •  exit
  •  break
