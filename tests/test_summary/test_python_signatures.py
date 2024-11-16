# tests/test_summary/test_python_signatures.py
import pytest
from llamero.summary.python_signatures import SignatureExtractor, generate_python_summary

def test_signature_extraction():
    """Test Python signature extraction."""
    source = """
def test_func(x: int, y: str = "default") -> bool:
    \"\"\"Test function.\"\"\"
    return True

class TestClass:
    \"\"\"Test class.\"\"\"
    def method(self, x: int) -> None:
        \"\"\"Test method.\"\"\"
        pass
    """
    
    extractor = SignatureExtractor()
    signatures = extractor.extract_signatures(source)
    
    assert len(signatures) == 2
    
    # Check function signature
    func = signatures[0]
    assert func.name == "test_func"
    assert func.kind == "function"
    assert len(func.args) == 2
    assert func.returns == "bool"
    assert func.docstring == "Test function."
    
    # Check class signature
    cls = signatures[1]
    assert cls.name == "TestClass"
    assert cls.kind == "class"
    assert cls.docstring == "Test class."
    assert len(cls.methods) == 1
    
    # Check method signature
    method = cls.methods[0]
    assert method.name == "method"
    assert method.kind == "method"
    assert len(method.args) == 2  # including self
    assert method.returns == "None"
    assert method.docstring == "Test method."

def test_generate_python_summary(temp_project_dir):
    """Test Python summary generation."""
    summary = generate_python_summary(temp_project_dir)
    
    # Check summary content
    assert "# Python Project Structure" in summary
    assert "def hello()" in summary
    assert "class TestClass:" in summary
    assert "def method(self)" in summary
