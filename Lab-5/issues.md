# Lab 5 – Issues Found and Fixed (`dairy_collection.py`)

Line numbers refer to the original file. Ordered by severity (Bandit High → Medium, then Pylint/Flake8).

| # | Issue | Tool / Code | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|---------|-------------|--------------|
| 1 | OS command injection | Bandit B605 (High) | Security | 31 | `os.system("echo printing slip for " + farmer)` passes user data to a shell. A farmer name like `Gopal; rm -rf ~` runs the second command. Verified: `printSlip("Gopal; echo INJECTED")` executed the injected command. | The shell was only being used to print text, so replaced it with `print()`. Removed the now-unused `os` import. |
| 2 | Weak hash (MD5) | Bandit B324 (High) | Security | 16 | `hashlib.md5` is cryptographically broken (practical collisions). | Switched to `hashlib.sha256`. Note: an unsalted hash of a name is still guessable by anyone who knows the name; if the token were used for authentication, `hmac` with a secret key or `secrets.token_hex()` would be the right choice. |
| 3 | SQL injection | Bandit B608 (Medium) | Security / Bug | 11 | `INSERT` built with `str.format()`. Verified: farmer name `Ravi', 999, 9.9, 'Mon') --` inserted a forged 999-litre row and made Ravi top farmer. A legitimate name like `O'Brien` crashed the program with a syntax error. | Parameterised query with `?` placeholders and a values tuple, so sqlite3 treats input as data, never SQL. |
| 4 | Unused import | Flake8 F401 / Pylint W0611 | Style | 2 | `json` imported but never used. | Removed the import. |
| 5 | Lines too long | Flake8 E501 / Pylint C0301 | Style | 7, 11, 20, 25 | Lines of 83–124 chars exceed PEP 8's 79-char limit. | Wrapped calls across lines and split SQL strings using implicit string concatenation. |
| 6 | Ambiguous variable name | Flake8 E741 | Style | 26 | `l` is easily confused with `1` and `I`. | Renamed to `best`. |
| 7 | Comparison to None | Flake8 E711 / Pylint C0121 | Bug-prone | 36 | `fat == None` can be overridden by `__eq__`; identity check is the correct test for the `None` singleton. | Changed to `fat is None`. |
| 8 | Non-snake_case names | Pylint C0103 | Convention | 10, 15, 19, 24, 30, 34 | `recordMilk`, `farmerToken`, etc. violate PEP 8 function naming. | Renamed to `record_milk`, `farmer_token`, `daily_total`, `top_farmer`, `print_slip`, `low_fat`. |
| 9 | Missing docstrings | Pylint C0114 / C0116 | Documentation | 1, 10–39 | No module or function docstrings. | Added a module docstring and a one-line docstring to every function. |
| 10 | Global `conn` shadowed by parameter | Pylint W0621 | Design | 6, 10, 19, 24, 34 | A module-level connection is created at import time and every function parameter shadows it, making it easy to use the wrong one. | Moved table creation into `create_ledger()`; `main()` creates a local connection and closes it at the end. |
| 11 | Old-style string formatting | Pylint C0209 | Convention | 11, 21 | `%` / `.format()` where an f-string is clearer. | Line 11 became a parameterised query (#3); line 21 now uses an f-string. |
| 12 | Code runs on import | Not flagged by any tool | Design | 47 | `main()` is called unconditionally, so `import dairy_collection` runs the demo and touches the database. | Wrapped in `if __name__ == "__main__":`. |
| 13 | Crash on empty ledger | Not flagged by any tool | Bug | 26 | `max()` on an empty result raises `ValueError` when no milk has been recorded. | `top_farmer()` returns `None` when there are no rows. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 2.00/10 (24 messages) | 10.00/10 |
| Flake8 | 7 issues | 0 |
| Bandit | 3 issues (2 High, 1 Medium) | 0 |

Program output is unchanged apart from the token, which is now a SHA-256 digest instead of MD5.
