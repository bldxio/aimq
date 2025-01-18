# Contributing to AIMQ

We love your input! We want to make contributing to AIMQ as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows our coding conventions
6. Issue that pull request!

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aimq.git
   cd aimq
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Running Tests

We use pytest for our test suite:

```bash
poetry run pytest
```

For coverage report:

```bash
poetry run pytest --cov=src
```

## Code Style

We follow these coding conventions:

1. **Type Hints**
   - All function parameters and return values must have type hints
   - Use `Optional` for parameters that can be None
   - Use `Union` for parameters that can be multiple types

2. **Docstrings**
   - All public functions, classes, and modules must have docstrings
   - Use Google style docstrings
   - Include Args, Returns, and Raises sections

3. **Naming Conventions**
   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Variables: snake_case
   - Constants: SCREAMING_SNAKE_CASE

## Pull Request Process

1. Update the README.md with details of changes to the interface
2. Update the documentation with any new features or changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
