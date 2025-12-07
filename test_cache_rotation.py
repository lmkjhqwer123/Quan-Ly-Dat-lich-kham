"""
Test API Key Caching & Rotation
"""
import sys
sys.path.insert(0, '.')

from routers.chatbot.chatbot_service import ChatbotService, _response_cache, _current_key_index, _api_keys

def test_caching():
    """Test response caching"""
    print("\n=== TEST RESPONSE CACHING ===")
    service = ChatbotService()
    
    test_message = "Tôi muốn khám bệnh"
    
    print(f"API Keys loaded: {len(_api_keys)}")
    print(f"Current key index: {_current_key_index}")
    print(f"\nTest message: '{test_message}'")
    
    # First call (will hit API)
    print("\n[CALL 1] First call - should hit API (or cache/fallback)")
    try:
        response1, tool1, tool_resp1 = service.process_message(test_message)
        print(f"Response: {response1[:100]}...")
        print(f"Tool used: {tool1}")
    except Exception as e:
        print(f"Error: {str(e)[:100]}")
    
    # Check cache
    print(f"\nCache status: {len(_response_cache)} items")
    
    # Second call (should use cache)
    print("\n[CALL 2] Same message - should use CACHE")
    try:
        response2, tool2, tool_resp2 = service.process_message(test_message)
        print(f"Response: {response2[:100]}...")
        print(f"Tool used: {tool2}")
        print(f"Cache hit: {response1 == response2}")
    except Exception as e:
        print(f"Error: {str(e)[:100]}")

if __name__ == "__main__":
    test_caching()
