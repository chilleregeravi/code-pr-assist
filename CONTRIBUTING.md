# Contributing to github-agent

Thank you for your interest in contributing to the project! Please follow these guidelines to help us review your changes quickly and effectively.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up the virtual environment:**
   ```sh
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Install in development mode:**
   ```sh
   pip install -e .
   ```

## Running Tests

Run all tests and check coverage:
```sh
make test
```

## Type Checking

Check type annotations using mypy:
```sh
make type-check
```

## Linting

Run linting and code style checks:
```sh
make lint
```

## Submitting Changes

- Open a pull request with a clear description of your changes.
- Ensure all tests pass and code style checks succeed.
- Reference any related issues in your PR description.

## Code Style

- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) guidelines.
- Use type annotations where possible.
- Keep functions and classes well-documented.

## Need Help?

If you have questions, open an issue or reach out to the maintainers. 