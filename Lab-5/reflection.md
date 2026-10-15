Lab 5 - Reflection

1. Which issues were the easiest to fix, and which were the hardest? Why?

The Flake8 ones were the easiest, like removing the unused import and changing == None to is None. The hardest was the global conn warning from Pylint because I had to move the database setup into a function and change main().

2. Did the static analysis tools report any false positives? If so, describe one example.

Not really. All the Bandit issues were real. The MD5 one could be a false positive if the hash is not used for security, but I changed it anyway. The tools also missed that topFarmer() crashes when the table is empty.

3. How would you integrate static analysis tools into your actual software development workflow?

I would run them before committing using a pre-commit hook, and also run them in GitHub Actions on every push so bad code does not get merged.

4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

The code is safer since SQL and shell injection are fixed. It is easier to read because of the better names and docstrings. The Pylint score went from 2.00 to 10.00.
