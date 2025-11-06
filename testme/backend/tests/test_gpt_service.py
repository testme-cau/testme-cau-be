"""
Test GPT Service

Run with: python -m pytest tests/test_gpt_service.py -v
Or: python tests/test_gpt_service.py (standalone)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.gpt_service import GPTService


def test_gpt_simple_call():
    """Test basic GPT API call"""
    print("\n=== Test 1: Simple GPT API Call ===")
    
    try:
        # Check if API key exists
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  SKIPPED: OPENAI_API_KEY not set")
            print("   Set your API key in .env file")
            return False
        
        # Initialize service
        gpt_service = GPTService(api_key=api_key)
        print(f"✓ GPTService initialized with model: {gpt_service.model}")
        
        # Simple test call
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use mini for testing (cheaper)
            messages=[
                {"role": "user", "content": "Say 'test successful' if you can read this."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✓ API Response: {result}")
        print("✅ Test PASSED: Basic GPT API call works")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_gpt_json_response():
    """Test GPT JSON response format"""
    print("\n=== Test 2: JSON Response Format ===")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  SKIPPED: OPENAI_API_KEY not set")
            return False
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You respond in JSON format only."},
                {"role": "user", "content": 'Return JSON: {"status": "ok", "message": "test"}'}
            ],
            response_format={"type": "json_object"},
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"✓ JSON Response: {result}")
        
        # Parse JSON
        import json
        data = json.loads(result)
        print(f"✓ Parsed JSON: {data}")
        print("✅ Test PASSED: JSON response format works")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_exam_generation_mock():
    """Test exam generation with mock PDF text"""
    print("\n=== Test 3: Exam Generation (Mock) ===")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  SKIPPED: OPENAI_API_KEY not set")
            return False
        
        gpt_service = GPTService(api_key=api_key)
        
        # Mock PDF text
        mock_text = """
        Python Programming Basics
        
        Variables and Data Types:
        - Integer: whole numbers
        - String: text data
        - Float: decimal numbers
        - Boolean: True or False
        
        Control Flow:
        - if/else statements
        - for loops
        - while loops
        """
        
        print("✓ Generating exam from mock PDF text...")
        result = gpt_service.generate_exam_from_text(
            mock_text,
            num_questions=3,
            difficulty="easy"
        )
        
        if result['success']:
            exam = result['exam']
            print(f"✓ Generated {len(exam['questions'])} questions")
            print(f"✓ Total points: {exam['total_points']}")
            print(f"✓ Estimated time: {exam['estimated_time']} minutes")
            
            # Show first question
            if exam['questions']:
                q1 = exam['questions'][0]
                print(f"\n  Sample Question:")
                print(f"  Type: {q1.get('type')}")
                print(f"  Question: {q1.get('question')[:100]}...")
                print(f"  Points: {q1.get('points')}")
            
            print("✅ Test PASSED: Exam generation works")
            return True
        else:
            print(f"❌ Test FAILED: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def test_grading_mock():
    """Test answer grading with mock data"""
    print("\n=== Test 4: Answer Grading (Mock) ===")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  SKIPPED: OPENAI_API_KEY not set")
            return False
        
        gpt_service = GPTService(api_key=api_key)
        
        # Mock question and answer
        question = "What is a variable in Python?"
        answer = "A variable is a container that stores data values."
        
        print("✓ Grading mock answer...")
        result = gpt_service.grade_answer(question, answer)
        
        if result['success']:
            grade = result['grade']
            print(f"✓ Score: {grade['score']}/100")
            print(f"✓ Correct: {grade['is_correct']}")
            print(f"✓ Feedback: {grade['feedback'][:100]}...")
            print("✅ Test PASSED: Answer grading works")
            return True
        else:
            print(f"❌ Test FAILED: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("GPT SERVICE TEST SUITE")
    print("="*60)
    
    results = {
        "Simple API Call": test_gpt_simple_call(),
        "JSON Response": test_gpt_json_response(),
        "Exam Generation": test_exam_generation_mock(),
        "Answer Grading": test_grading_mock()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)

