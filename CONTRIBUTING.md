# Contributing to CriptoBot

Thank you for considering contributing to CriptoBot! This document outlines the process for contributing to the project and the standards expected from contributors.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and collaborative environment.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please search existing issues to see if the problem has already been reported. If it hasn't, create a new issue using the bug report template.

When filing a bug report, please include:
- A clear and descriptive title
- Detailed steps to reproduce the issue
- Expected behavior vs actual behavior
- Any relevant logs or screenshots
- Your system information (Python version, operating system, etc.)

### Suggesting Enhancements

If you have ideas for improving CriptoBot, we'd love to hear them! Please create a feature request using the provided template and include:
- A clear and concise description of what you want to happen
- Any potential implementation ideas you might have
- Why this enhancement would be useful to most CriptoBot users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure your code follows the style guidelines
5. Test your changes thoroughly
6. Commit your changes with clear commit messages
7. Push to your branch
8. Open a Pull Request against the main branch

## Development Workflow

### Setting Up Development Environment

1. Clone your fork of the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create your own `config.py` based on `config.example.py`

### Code Style

We follow PEP 8 style guidelines for Python code. Please ensure your code:
- Uses 4 spaces for indentation (not tabs)
- Keeps lines to a maximum of 88 characters
- Includes docstrings for all functions, classes and modules
- Uses meaningful variable and function names
- Has appropriate comments for complex code sections

### Testing

Before submitting a PR, please test your changes with:
- Both paper trading and real trading modes (if applicable)
- Different market conditions if possible
- Edge cases like connection failures, API errors, etc.

## Contribution Guidelines for Trading Strategy Improvements

When modifying or adding trading strategies:
1. Document the strategy clearly, explaining the indicators used and the rationale
2. Include backtest results if possible
3. Explicitly state the risk factors and limitations
4. Ensure all parameters are configurable
5. Add appropriate logging for strategy decision points

## Financial and Legal Considerations

- Never include real API keys, account information, or trading history in contributions
- Be clear about the risks involved in any strategy you contribute
- Respect exchange APIs' terms of service and rate limits

## Getting Help

If you need help with your contribution, feel free to ask questions in the issues or discussions section of the repository.

Thank you for contributing to CriptoBot!

