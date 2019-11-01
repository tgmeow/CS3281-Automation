# CS3281 Github Utility

This is a basic python3 utility program to help with batch git clone, push, and a few other operations.   
## Installation and Running
You need python3 with pip.   
I am using pipenv to manage dependencies.   
```
pipenv install
pipenv shell
python3 CS3281Automation.py
```


## Basic Usage  
The program runs a primitive/clunky REPL.   
Basic commands:
- q    - exit   
- activate #   - "opens" an assignment # for grading. Prompts for grading group and clones the assignment from github if the directory does not exist.   
- status  - prints the current activated assignment.   
- print_grades  - prints the "grade.md" of each repository under the current activated assignment.   
- push_grading  - adds, commits, and pushes the file "grade.md" for each repository under the current activated assignment.   
- check_commits  - checks github for new commits for the current assignment.   
- check_commit_date   - prints the commit date of the latest commit for each repository for the current assignment.   
- help   - doesn't do anything

### Example usage
```bash
python3 CS3281Automation.py

# Clone grading group 2 for assignment 6:
activate 6
y
3

# Check commit dates for late days
check_commit_date

# When done grading, print the grades for the current assignment (or for entering in gradebook)
print_grades

# When everything looks good, push to github
push_grading

# Exit the program
q
```

*Screenshot* 
![screenshot of example](https://raw.githubusercontent.com/tgmeow/CS3281-Automation/master/Example1.PNG)
