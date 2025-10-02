#!/bin/bash
# Run tests with coverage

echo "Running tests..."
pytest tests/ -v --tb=short

echo ""
echo "Tests completed!"