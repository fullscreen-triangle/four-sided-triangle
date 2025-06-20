#!/bin/bash

# Build script for Four-Sided Triangle Rust components
# This script builds the Rust components and integrates them with Python

set -e  # Exit on any error

echo "🦀 Building Four-Sided Triangle Rust Components"
echo "=============================================="

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo not found. Please install Rust from https://rustup.rs/"
    exit 1
fi

echo "✅ Rust installation found"

# Check if Python development dependencies are installed
echo "📦 Checking Python dependencies..."

# Install development dependencies if needed
if ! python -c "import setuptools_rust" &> /dev/null; then
    echo "📦 Installing setuptools-rust..."
    pip install setuptools-rust
fi

if ! python -c "import maturin" &> /dev/null; then
    echo "📦 Installing maturin..."
    pip install maturin
fi

echo "✅ Python build dependencies ready"

# Build Rust components in release mode
echo "🔨 Building Rust components (release mode)..."
cargo build --release

echo "✅ Rust components built successfully"

# Build Python extension
echo "🐍 Building Python extension..."
python setup.py build_ext --inplace

echo "✅ Python extension built successfully"

# Optional: Run tests
if [ "$1" = "--with-tests" ]; then
    echo "🧪 Running Rust tests..."
    cargo test --release
    
    echo "🧪 Running Python integration tests..."
    python -c "
import sys
import json
try:
    import four_sided_triangle_core
    print('✅ Rust module imported successfully')
    
    # Test basic functions
    result = four_sided_triangle_core.py_calculate_text_similarity('hello world', 'hello rust')
    print(f'✅ Text similarity test passed: {result}')
    
    # Test fuzzy evidence system
    fuzzy_set = four_sided_triangle_core.py_create_fuzzy_set(
        'test_set', 0.0, 1.0, 
        json.dumps({'type': 'triangular', 'left': 0.0, 'center': 0.5, 'right': 1.0})
    )
    print('✅ Fuzzy set creation test passed')
    
    # Test evidence network
    network_id = four_sided_triangle_core.py_create_evidence_network()
    print(f'✅ Evidence network creation test passed: {network_id}')
    
    # Test metacognitive optimizer
    optimizer_id = four_sided_triangle_core.py_create_optimizer()
    print(f'✅ Metacognitive optimizer creation test passed: {optimizer_id}')
    
    print('✅ All fuzzy evidence system tests passed')
    
except ImportError as e:
    print(f'❌ Failed to import Rust module: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    sys.exit(1)
"
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "You can now use the high-performance Rust components in your Python code:"
echo ""
echo "  from app.core.rust_integration import rust_integration"
echo "  result = rust_integration.detect_throttling(response, query)"
echo ""
echo "If the Rust module fails to load, the system will automatically"
echo "fall back to Python implementations." 