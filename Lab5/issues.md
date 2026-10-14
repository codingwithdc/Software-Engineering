# Static Analysis Issues

| # | Issue | Tool / Code | Type | Severity | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|----------|---------|-------------|--------------|
| 1 | Unsafe tar extraction | Bandit B202 | Security | High | 63-64 | `extractall` on a customer archive allows path traversal outside `claims_docs` | `extractall(filter="data")` in a `with` block |
| 2 | Unverified SSL context | Bandit B323, Pylint W0212 | Security | Medium | 58 | Certificate checks disabled, so MITM is possible | `ssl.create_default_context()` |
| 3 | Unrestricted urlopen | Bandit B310 | Security | Medium | 59 | `file://` and custom schemes are allowed | Allow only `https://`; add a timeout |
| 4 | Unsafe XML parsing | Bandit B314, B405 | Security | Medium | 7, 48 | ElementTree is vulnerable to XML bomb / XXE attacks | Use `defusedxml.ElementTree` |
| 5 | Bind to all interfaces | Bandit B104 | Security | Medium | 12 | `0.0.0.0` exposes the service on every network | Default to `127.0.0.1` |
| 6 | Hardcoded temp path | Bandit B108 | Security | Medium | 14 | Log in world-writable `/tmp` | Write the log in the working directory |
| 7 | Hardcoded secret | Bandit B105 | Security | Low | 13, 103 | Token is in the source and in `main()` | Read from an env var; `hmac.compare_digest` |
| 8 | Insecure random | Bandit B311 | Security | Low | 37 | Policy numbers are predictable | `secrets.randbelow` |
| 9 | Mutable default arg | Pylint W0102 | Bug | Medium | 17, 27 | `discounts=[]` is shared across calls, so identical quotes differ (6000 vs 5500) | Default to `None`; don't append |
| 10 | Bare except | Pylint W0702, Flake8 E722, Bandit B112 | Bug | Medium | 53-54 | Catches everything and silently skips rows | `except (TypeError, ValueError)` |
| 11 | Truthy string as bool | Manual | Logic | Medium | 22, 92 | `"no"` is treated as smoker, so the quote is 7970 instead of 6900 | Pass `False`; validate it is a bool |
| 12 | Wrong age | Manual | Logic | Medium | 33 | Ignores whether the birthday has passed (36 instead of 35) | Subtract 1 if the birthday hasn't come yet |
| 13 | Negative premium | Manual | Logic | Medium | 25-26 | Discounts can push the premium below 0 (-800) | `max(premium, 0)` |
| 14 | File not closed safely | Pylint R1732, W1514 | Bug | Low | 42-44 | File leaks on error; no encoding given | `with open(..., encoding="utf-8")` |
| 15 | Instalment rounding | Manual | Logic | Low | 67-71 | `floor` loses money; `months=0` is accepted | `round(..., 2)`; reject months ≤ 0 |
| 16 | Leap-year renewal crash | Manual | Logic | Low | 81 | 29 Feb + 1 year raises `ValueError` | Fall back to 28 Feb |
| 17 | Naming / docstrings | Pylint C0103, C0114, C0116 | Style | Low | all | camelCase names, no docstrings | snake_case; add docstrings |
| 18 | PEP 8 formatting | Flake8 E302, E305, E501 | Style | Low | many | Missing blank lines, long lines | 2 blank lines; wrap lines; `__main__` guard |