import json

def convert_to_json(input_data):
    """
    Convert data to JSON format and print it to console.
    
    Args:
        input_data: String to be parsed as JSON or a Python object to be converted to JSON
        
    Returns:
        dict/list/None: The parsed JSON data if successful, None if parsing fails
    """
    try:
        # Check if input is already a dict or list (already parsed)
        if isinstance(input_data, (dict, list)):
            json_data = input_data
        else:
            # Try to parse the string as JSON
            json_data = json.loads(input_data)
        
        # Print the formatted JSON to console
        print("Converted JSON:")
        # print(json.dumps(json_data, indent=2))
        
        return json_data
    
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error: Invalid JSON input - {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Example string that is valid JSON
    example_json_string = '{"name": "John", "age": 30, "city": "New York"}'
    convert_to_json(example_json_string)
    
    # Example string that is not valid JSON
    invalid_json = '{name: John, age: 30}'
    convert_to_json(invalid_json)
    
    # Example with dictionary input
    dict_input = {"name": "John", "age": 30, "city": "New York"}
    convert_to_json(dict_input)
