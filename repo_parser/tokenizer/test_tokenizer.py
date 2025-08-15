import ctypes, os
import sqlite3

# Load the correct extension
con = sqlite3.connect(":memory:")
con.enable_load_extension(True)

ext_path = os.path.abspath("repo_parser/tokenizer/mytokenizer")
try:
    con.load_extension(ext_path)
    print("✓ Successfully loaded C extension")
except Exception as e:
    print(f"✗ Error loading C extension: {e}")
    exit(1)

# Test FTS5 functionality with custom tokenizer
try:
    # Create a virtual table with our custom tokenizer
    con.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content, tokenize='mytokenizer')")
    print("✓ Successfully created FTS5 table with custom tokenizer")
    
    # Test data with various tokenization scenarios
    test_inputs = [
        "helloWorld",           # camelCase
        "hello_world",          # snake_case
        "HelloWorld",           # PascalCase
        "hello_world_test",     # multiple underscores
        "camelCase_with_underscores",  # mixed
        "UPPER_CASE",           # all caps with underscores
        "lowercase",            # all lowercase
        "UPPERCASE",            # all uppercase
        "camelCase123",         # with numbers
        "test123_456",          # numbers with underscores
        "special@chars#here",   # special characters
        "mixedCase_with_123_and_underscores",  # complex case
        "APIEndpoint",          # acronyms
        "userID123",            # acronyms with numbers
        "getUserById",          # method names
        "class MyClass",        # with spaces
        "function testFunction()",  # function syntax
        "variable_name_123",    # typical variable
        "CONSTANT_VALUE",       # constants
        "enum ColorType",       # enum syntax
    ]
    
    print("\n" + "="*60)
    print("TOKENIZATION TEST RESULTS")
    print("="*60)
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{i:2d}. Input: '{test_input}'")
        
        # Insert the test data
        con.execute("INSERT INTO test_fts(content) VALUES (?)", (test_input,))
        
        # Query to see how it was tokenized
        # We'll use a simple query to see what tokens are searchable
        cursor = con.execute("SELECT content FROM test_fts WHERE test_fts MATCH 'test'")
        # This won't show tokens directly, so let's use a different approach
        
        # Use the tokenizer directly through FTS5 auxiliary functions
        try:
            # Try to get tokens using FTS5 highlight function
            cursor = con.execute("""
                SELECT highlight(test_fts, 0, '<', '>') 
                FROM test_fts 
                WHERE rowid = ?
            """, (i,))
            result = cursor.fetchone()
            if result:
                print(f"    Highlighted: {result[0]}")
        except:
            pass
        
        # Alternative: Use FTS5 snippet function
        try:
            cursor = con.execute("""
                SELECT snippet(test_fts, 0, '<', '>', '...', 10) 
                FROM test_fts 
                WHERE rowid = ?
            """, (i,))
            result = cursor.fetchone()
            if result:
                print(f"    Snippet: {result[0]}")
        except:
            pass
    
    # Test specific token searches to see what gets matched
    print(f"\n" + "="*60)
    print("TOKEN SEARCH TESTS")
    print("="*60)
    
    search_tests = [
        ("hello", "Should match 'hello' in various forms"),
        ("world", "Should match 'world' in various forms"),
        ("camel", "Should match 'camel' from camelCase"),
        ("case", "Should match 'case' from various forms"),
        ("user", "Should match 'user' from getUserById"),
        ("api", "Should match 'api' from APIEndpoint"),
        ("123", "Should match numbers"),
        ("test", "Should match 'test' in various contexts"),
    ]
    
    for search_term, description in search_tests:
        print(f"\nSearching for '{search_term}': {description}")
        cursor = con.execute("SELECT content FROM test_fts WHERE test_fts MATCH ?", (search_term,))
        results = cursor.fetchall()
        if results:
            for result in results:
                print(f"    ✓ Found: {result[0]}")
        else:
            print(f"    ✗ No matches found")
    
    # More detailed token analysis using individual word searches
    print(f"\n" + "="*60)
    print("DETAILED TOKEN ANALYSIS")
    print("="*60)
    
    # Test individual components to see what tokens are created
    detailed_tests = [
        ("helloWorld", ["hello", "world"]),
        ("camelCase", ["camel", "case"]),
        ("APIEndpoint", ["api", "endpoint"]),
        ("userID123", ["user", "id", "123"]),
        ("getUserById", ["get", "user", "by", "id"]),
        ("mixedCase_with_123", ["mixed", "case", "with", "123"]),
    ]
    
    for test_input, expected_tokens in detailed_tests:
        print(f"\nTesting: '{test_input}'")
        print(f"Expected tokens: {expected_tokens}")
        
        # Test each expected token
        found_tokens = []
        for token in expected_tokens:
            cursor = con.execute("SELECT content FROM test_fts WHERE test_fts MATCH ?", (token,))
            results = cursor.fetchall()
            if results:
                for result in results:
                    if result[0] == test_input:
                        found_tokens.append(token)
                        break
        
        if found_tokens:
            print(f"✓ Found tokens: {found_tokens}")
        else:
            print(f"✗ No expected tokens found")
    
    # Test edge cases
    print(f"\n" + "="*60)
    print("EDGE CASE TESTING")
    print("="*60)
    
    edge_cases = [
        "single",           # single word
        "a",                # single letter
        "123",              # numbers only
        "_underscore_",     # leading/trailing underscores
        "camelCase123",     # camelCase with numbers
        "UPPER_CASE_123",   # uppercase with numbers
        "mixedCase123",     # mixed case with numbers
        "special@chars",    # special characters
        "  spaces  ",       # leading/trailing spaces
    ]
    
    for edge_case in edge_cases:
        print(f"\nEdge case: '{edge_case}'")
        try:
            con.execute("INSERT INTO test_fts(content) VALUES (?)", (edge_case,))
            print(f"✓ Inserted successfully")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n" + "="*60)
    print("CUSTOM TOKENIZER ANALYSIS")
    print("="*60)
    print("Based on the code analysis, your tokenizer:")
    print("1. Splits on non-alphanumeric characters (except underscores)")
    print("2. Further splits on camelCase boundaries (lowercase → uppercase)")
    print("3. Converts all tokens to lowercase")
    print("4. Treats underscores as word separators")
    print("5. Handles numbers as part of tokens")
    print("\nExpected tokenization examples:")
    print("  'helloWorld' → ['hello', 'world']")
    print("  'hello_world' → ['hello', 'world']")
    print("  'camelCase_with_underscores' → ['camel', 'case', 'with', 'underscores']")
    print("  'APIEndpoint' → ['api', 'endpoint']")
    print("  'userID123' → ['user', 'id', '123']")

except Exception as e:
    print(f"✗ Error with FTS5: {e}")

con.close()
