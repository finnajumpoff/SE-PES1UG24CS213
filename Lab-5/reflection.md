# Lab 5 – Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues: removing the unused `json` import, renaming `l` to `best`, and changing `== None` to `is None`. Each was a one-line, mechanical change with no effect on behaviour.

The hardest was the Pylint `redefined-outer-name` warning on `conn`. It wasn't a single-line fix; it pointed at a design problem. The database connection was created at module level when the file was imported, and every function took a parameter with the same name. Fixing it properly meant moving table creation into a `create_ledger()` function, creating the connection inside `main()`, and adding an `if __name__ == "__main__":` guard so importing the module no longer runs the demo.

The security fixes needed the most thought about *intent*. For `os.system`, the question was what the shell call was for. It only echoed text, so `print()` was correct rather than swapping in `subprocess`. For MD5, swapping to SHA-256 silences Bandit, but an unsalted hash of a farmer's name is still predictable. If the token were ever used to authenticate someone, it would need an HMAC with a secret key instead.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no real false positives in this file. Every Bandit finding was exploitable when I tested it: a farmer name of `Ravi', 999, 9.9, 'Mon') --` inserted a forged 999-litre delivery, and `Gopal; echo INJECTED` ran a second shell command.

The closest to a false positive is B324 (MD5). Bandit can't know whether the hash is used for security; for a non-security checksum, MD5 with `usedforsecurity=False` would be acceptable. The more common false-positive pattern is B608 firing on f-strings that build SQL from constants only, such as table names, which Bandit can't distinguish from user input.

The tools also had **false negatives**. None of them flagged that `topFarmer()` crashes with `ValueError` on an empty table, or that `main()` ran on import. Static analysis catches patterns, not logic, so it doesn't replace testing.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor as I type, and add a `pre-commit` hook running Flake8 and Bandit so issues are caught before they're committed.
- **In CI:** a GitHub Actions job running all three tools on every pull request, failing the build on any Bandit Medium/High finding, any Flake8 error, or a Pylint score below a set threshold (for example 9.0).
- **Configuration:** a shared `.pylintrc` / `setup.cfg` so the whole team uses the same rules, with `# nosec` or `# pylint: disable=` only for reviewed exceptions, each with a comment explaining why.

The trade-off is noise. Too strict a configuration on an old codebase produces hundreds of warnings people learn to ignore, so it's better to enforce the rules on new or changed code first and tighten over time.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** all three Bandit findings are gone; SQL and shell injection are no longer possible through farmer names.
- **Robustness:** names with apostrophes like `O'Brien` now work instead of crashing, and `top_farmer()` returns `None` on an empty ledger instead of raising.
- **Readability:** snake_case names, docstrings, f-strings and a named `LOW_FAT_THRESHOLD` constant make the code self-explanatory.
- **Reusability and testability:** with no global connection and no code running on import, each function can be imported and tested against its own fresh database.
- **Scores:** Pylint went from 2.00 to 10.00, Flake8 from 7 issues to 0, and Bandit from 3 issues to 0, with the program's output otherwise unchanged.
