
try:
    from google import genai
    print("genai package available")
    import os
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        client = genai.Client(api_key=api_key)
        print("client initialized")
        # Try a simple prompt
        response = client.models.generate_content(model='gemini-2.0-flash-exp', contents="test")
        print(f"Response received: {response.text[:10]}")
    else:
        print("API key missing")
except Exception as e:
    print(f"Error: {e}")
