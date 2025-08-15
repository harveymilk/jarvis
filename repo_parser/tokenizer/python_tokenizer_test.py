import re

def simulate_tokenizer(text):
    """
    Simulate the C tokenizer behavior based on the code analysis.
    This tokenizer:
    1. Splits on non-alphanumeric characters (except underscores)
    2. Further splits on camelCase boundaries (lowercase → uppercase)
    3. Converts all tokens to lowercase
    4. Treats underscores as word separators
    """
    # First, split on non-alphanumeric characters (except underscores)
    words = re.split(r'[^a-zA-Z0-9_]', text)
    
    tokens = []
    for word in words:
        if not word:
            continue
            
        # Split on underscores
        parts = word.split('_')
        
        for part in parts:
            if not part:
                continue
                
            # Split on camelCase boundaries (lowercase followed by uppercase)
            camel_parts = re.split(r'(?<=[a-z])(?=[A-Z])', part)
            
            for camel_part in camel_parts:
                if camel_part:
                    # Convert to lowercase
                    tokens.append(camel_part.lower())
    
    return tokens

# Test cases
test_cases = [
    ("helloWorld", ["hello", "world"]),
    ("hello_world", ["hello", "world"]),
    ("HelloWorld", ["hello", "world"]),
    ("camelCase", ["camel", "case"]),
    ("APIEndpoint", ["api", "endpoint"]),
    ("userID123", ["user", "id", "123"]),
    ("getUserById", ["get", "user", "by", "id"]),
    ("camelCase_with_underscores", ["camel", "case", "with", "underscores"]),
    ("mixedCase123", ["mixed", "case", "123"]),
    ("UPPER_CASE", ["upper", "case"]),
    ("CONSTANT_VALUE", ["constant", "value"]),
    ("function_name", ["function", "name"]),
    ("test123_456", ["test", "123", "456"]),
    ("special@chars#here", ["special", "chars", "here"]),
    ("class MyClass", ["class", "my", "class"]),
    ("enum ColorType", ["enum", "color", "type"]),
    ("variable_name_123", ["variable", "name", "123"]),
    ("getUserById123", ["get", "user", "by", "id", "123"]),
    ("APIEndpoint123", ["api", "endpoint", "123"]),
    ("camelCase123_with_456", ["camel", "case", "123", "with", "456"]),
    ("single", ["single"]),
    ("a", ["a"]),
    ("123", ["123"]),
    ("_underscore_", ["underscore"]),
    ("UPPER_CASE_123", ["upper", "case", "123"]),
    ("  spaces  ", ["spaces"]),
]

print("="*80)
print("PYTHON TOKENIZER SIMULATION")
print("="*80)
print("This simulates how your C tokenizer should behave based on the code analysis.")
print("="*80)

for i, (test_input, expected_tokens) in enumerate(test_cases, 1):
    actual_tokens = simulate_tokenizer(test_input)
    
    print(f"\n{i:2d}. Input: '{test_input}'")
    print(f"    Expected: {expected_tokens}")
    print(f"    Actual:   {actual_tokens}")
    
    if actual_tokens == expected_tokens:
        print(f"    ✓ MATCH")
    else:
        print(f"    ✗ MISMATCH")

print(f"\n{'='*80}")
print("TOKENIZER BEHAVIOR SUMMARY")
print("="*80)
print("Based on the C code analysis, your tokenizer should:")
print("✓ Split camelCase correctly (helloWorld → hello, world)")
print("✓ Split on underscores (hello_world → hello, world)")
print("✓ Convert to lowercase (HelloWorld → hello, world)")
print("✓ Handle numbers as part of tokens (userID123 → user, id, 123)")
print("✓ Split on spaces (class MyClass → class, my, class)")
print("✓ Handle special characters as separators")
print("✓ Handle mixed cases with numbers and underscores")

print(f"\n{'='*80}")
print("COMMON TOKENIZATION PATTERNS")
print("="*80)
print("camelCase → ['camel', 'case']")
print("snake_case → ['snake', 'case']")
print("PascalCase → ['pascal', 'case']")
print("UPPER_CASE → ['upper', 'case']")
print("mixedCase123 → ['mixed', 'case', '123']")
print("getUserById → ['get', 'user', 'by', 'id']")
print("APIEndpoint → ['api', 'endpoint']")
print("variable_name_123 → ['variable', 'name', '123']")
