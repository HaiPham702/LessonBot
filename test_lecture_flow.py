#!/usr/bin/env python3
"""
Test Lecture Creation Flow với dàn ý chi tiết
"""
import requests
import json

def test_lecture_creation_flow():
    """Test luồng tạo bài giảng mới"""
    print("🧪 Testing Detailed Lecture Creation Flow...")
    print("=" * 60)
    
    # Create new session
    print("\n📝 Step 1: Create New Session")
    try:
        response = requests.post("http://localhost:8000/api/v1/chat/session")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["id"]
            print(f"✅ Session created: {session_id}")
        else:
            print(f"❌ Failed to create session: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test lecture creation request
    print(f"\n💬 Step 2: Request Lecture Creation")
    try:
        lecture_request = {
            "message": "Tôi muốn tạo bài giảng về Phân số cho học sinh lớp 6. Bao gồm khái niệm cơ bản, các phép tính với phân số, và bài tập thực hành.",
            "sessionId": session_id
        }
        
        print(f"📤 Request: {lecture_request['message']}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat/message",
            json=lecture_request,
            timeout=60
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received")
            print(f"   Reply: {result['reply'][:100]}...")
            
            # Check if metadata contains lecture data
            metadata = result.get('metadata', {})
            if metadata.get('type') == 'lecture':
                print(f"✅ Lecture type detected!")
                lecture_data = metadata.get('lecture_data', {})
                
                print(f"\n📋 Lecture Structure:")
                print(f"   Title: {lecture_data.get('title', 'N/A')}")
                print(f"   Subject: {lecture_data.get('subject', 'N/A')}")
                print(f"   Grade: {lecture_data.get('grade', 'N/A')}")
                print(f"   Duration: {lecture_data.get('duration', 'N/A')}")
                
                objectives = lecture_data.get('objectives', [])
                print(f"   Objectives: {len(objectives)} items")
                for i, obj in enumerate(objectives[:2]):
                    print(f"     {i+1}. {obj}")
                
                outline = lecture_data.get('outline', [])
                print(f"   Outline: {len(outline)} sections")
                for i, section in enumerate(outline[:2]):
                    print(f"     Section {i+1}: {section.get('section', 'N/A')}")
                    topics = section.get('topics', [])
                    print(f"       Topics: {len(topics)} items")
                
                if metadata.get('show_create_slide_button'):
                    print(f"✅ Create slide button should be shown")
                
                if metadata.get('editable'):
                    print(f"✅ Lecture is editable")
                
            else:
                print(f"❌ Not a lecture response. Type: {metadata.get('type', 'unknown')}")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test get chat history to verify storage
    print(f"\n📜 Step 3: Verify Chat History Storage")
    try:
        response = requests.get(f"http://localhost:8000/api/v1/chat/history/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            messages = result.get("messages", [])
            print(f"✅ Found {len(messages)} messages in history")
            
            for msg in messages:
                msg_type = msg.get("message_type", "text")
                sender = msg.get("sender", "unknown")
                has_metadata = bool(msg.get("metadata"))
                
                print(f"   {sender}: type={msg_type}, has_metadata={has_metadata}")
                
                if msg_type == "lecture" and has_metadata:
                    metadata = msg.get("metadata", {})
                    lecture_data = metadata.get("lecture_data", {})
                    print(f"     ✅ Lecture data preserved: {lecture_data.get('title', 'N/A')}")
        else:
            print(f"❌ Failed to get history: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Lecture Creation Flow Testing Complete!")

def test_services_health():
    """Test all services are running"""
    print("🏥 Checking Services Health...")
    
    services = [
        ("Backend", "http://localhost:8000/health"),
        ("Main Agent", "http://localhost:8001/health")
    ]
    
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy ({response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: Offline ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    if test_services_health():
        print()
        test_lecture_creation_flow()
    else:
        print("\n❌ Some services are not healthy. Please start all services first.")
