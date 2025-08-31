import os
import glob
import importlib.util
from typing import List, Callable, Tuple, Dict

class VerificationFramework:
    """
    A modular framework for running multiple code verification functions.
    Automatically discovers verification functions in the current directory.
    """
    
    def __init__(self, verify_dir: str = "."):
        """
        Initialize the verification framework.
        
        Args:
            verify_dir: Directory to search for verification files
        """
        self.verify_dir = verify_dir
        self.verifiers = {}
        self._discover_verifiers()
    
    def _discover_verifiers(self):
        """Automatically discover verification functions in Python files."""
        # Look for Python files that start with "verify-"
        pattern = os.path.join(self.verify_dir, "verify-*.py")
        verify_files = glob.glob(pattern)
        
        for file_path in verify_files:
            file_name = os.path.basename(file_path)
            module_name = file_name[:-3]  # Remove .py extension
            
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for functions that start with "verify"
                for attr_name in dir(module):
                    if attr_name.startswith('verify') and callable(getattr(module, attr_name)):
                        func = getattr(module, attr_name)
                        # Check if it takes exactly one parameter (code)
                        import inspect
                        sig = inspect.signature(func)
                        if len(sig.parameters) == 1:
                            self.verifiers[attr_name] = {
                                'function': func,
                                'module': module_name,
                                'file': file_name
                            }
                            
            except Exception as e:
                print(f"Warning: Could not load verifier from {file_name}: {e}")
    
    def run_all_verifiers(self, code: str) -> Dict[str, bool]:
        """
        Run all discovered verification functions on the given code.
        
        Args:
            code: The code to verify
            
        Returns:
            Dictionary mapping verifier names to their results (True/False)
        """
        results = {}
        for verifier_name, verifier_info in self.verifiers.items():
            try:
                result = verifier_info['function'](code)
                results[verifier_name] = bool(result)
            except Exception as e:
                print(f"Error running {verifier_name}: {e}")
                results[verifier_name] = False
        
        return results
    
    def verify_code(self, code: str) -> Tuple[bool, Dict[str, bool]]:
        """
        Verify code using all available verifiers.
        
        Args:
            code: The code to verify
            
        Returns:
            Tuple of (all_passed, individual_results)
            all_passed is True only if ALL verifiers return True
        """
        results = self.run_all_verifiers(code)
        all_passed = all(results.values()) if results else False
        return all_passed, results
    
    def get_verifier_names(self) -> List[str]:
        """Get list of all discovered verifier function names."""
        return list(self.verifiers.keys())
    
    def get_verifier_info(self) -> Dict[str, Dict]:
        """Get detailed information about all discovered verifiers."""
        return {name: {
            'module': info['module'],
            'file': info['file']
        } for name, info in self.verifiers.items()}

def create_verification_framework(verify_dir: str = ".") -> VerificationFramework:
    """
    Convenience function to create a verification framework.
    
    Args:
        verify_dir: Directory to search for verification files
        
    Returns:
        Configured VerificationFramework instance
    """
    return VerificationFramework(verify_dir) 