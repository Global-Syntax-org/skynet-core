# filepath: c:\workspace\code\python\skynet-lite\\.github\workflows\ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run code quality checks
      run: |
        black --check .
        flake8 .
        mypy .
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run security scan
      uses: pypa/gh-action-pip-audit@v1.0.8
      with:
        inputs: requirements.txt