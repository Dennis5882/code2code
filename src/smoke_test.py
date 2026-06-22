# Smoke test for trigger #3: source-path normalization
# This file is a placeholder to verify the integration step.

def normalize_path(path: str) -> str:
    """
    Normalize a source file path by removing a leading '/' if present.
    Example: '/src/foo.py' -> 'src/foo.py'
    """
    if path.startswith('/'):
        return path[1:]
    return path

if __name__ == '__main__':
    test_path = '/src/foo.py'
    normalized = normalize_path(test_path)
    print(f'Original: {test_path}')
    print(f'Normalized: {normalized}')
    assert normalized == 'src/foo.py', 'Normalization failed'
    print('Smoke test passed.')
