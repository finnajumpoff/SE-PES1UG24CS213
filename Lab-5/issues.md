Lab 5 - Issues found in dairy_collection.py

| Issue | Type | Line | Description | Fix |
|---|---|---|---|---|
| os.system shell command | Security (Bandit B605, High) | 31 | farmer name is passed to the shell so extra commands can run | used print() instead and removed import os |
| MD5 hash | Security (Bandit B324, High) | 16 | md5 is a weak hash | changed to sha256 |
| SQL injection | Security (Bandit B608, Medium) | 11 | query is built with format() so input can change the query | used ? placeholders |
| Unused import | Style (Flake8 F401) | 2 | json is imported but not used | removed it |
| Lines too long | Style (Flake8 E501) | 7, 11, 20, 25 | lines longer than 79 characters | split them into multiple lines |
| Variable name l | Style (Flake8 E741) | 26 | l looks like 1 | renamed to best |
| == None | Style (Flake8 E711) | 36 | should use is None | changed to is None |
| Function names | Convention (Pylint C0103) | 10-34 | names were camelCase | changed to snake_case |
| No docstrings | Convention (Pylint C0114, C0116) | whole file | no docstrings | added docstrings |
| Global conn | Warning (Pylint W0621) | 6 | conn is global and also a parameter name | created conn inside main() |

Pylint score went from 2.00 to 10.00. Flake8 and Bandit show no issues after the fixes.
