"""
CampusCompass AI - Automated Test Suite
Executes all 10 mandatory test cases + paraphrased and follow-up tests.
"""

import unittest
import time
from app import app

class CampusCompassTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_00_health_endpoint(self):
        """Verify /api/health returns healthy and reports system status."""
        res = self.app.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "CampusCompass AI")
        print("✓ Health Check Passed: Service is healthy")

    def test_00_categories_endpoint(self):
        """Verify /api/categories returns all 8 categories."""
        res = self.app.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("categories")), 8)
        print("✓ Categories Check Passed: 8 categories returned")

    def _ask(self, question, session_id="test-session-1"):
        res = self.app.post("/api/chat", json={
            "message": question,
            "session_id": session_id
        })
        self.assertEqual(res.status_code, 200)
        return res.get_json()

    def test_TC01_academics(self):
        """TC01: Whom should I contact for academic problems? -> Faculty advisor"""
        data = self._ask("Whom should I contact for academic problems?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertIn("faculty advisor", answer)
        print(f"✓ TC01 Passed: {data['answer'][:70]}...")

    def test_TC02_examinations(self):
        """TC02: Where can I find the examination timetable? -> Official university channels"""
        data = self._ask("Where can I find the examination timetable?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("official" in answer or "channel" in answer)
        print(f"✓ TC02 Passed: {data['answer'][:70]}...")

    def test_TC03_placements(self):
        """TC03: Whom should I contact for placement training? -> Placement Department"""
        data = self._ask("Whom should I contact for placement training?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertIn("placement department", answer)
        print(f"✓ TC03 Passed: {data['answer'][:70]}...")

    def test_TC04_hostel(self):
        """TC04: How can I raise a hostel complaint? -> Hostel Administration"""
        data = self._ask("How can I raise a hostel complaint?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertIn("hostel administration", answer)
        print(f"✓ TC04 Passed: {data['answer'][:70]}...")

    def test_TC05_exam_date_unavailable(self):
        """TC05: What is the exact date of my next examination? -> Date unavailable"""
        data = self._ask("What is the exact date of my next examination?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("unavailable" in answer or "not available" in answer or "official" in answer)
        self.assertNotIn("2026", answer)
        print(f"✓ TC05 Passed: {data['answer'][:70]}...")

    def test_TC06_library_timings(self):
        """TC06: What are the library timings? -> Exact timings unavailable"""
        data = self._ask("What are the library timings?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("timing" in answer or "unavailable" in answer or "regulations" in answer)
        self.assertNotIn("9:00 am", answer)
        print(f"✓ TC06 Passed: {data['answer'][:70]}...")

    def test_TC07_fee_structure(self):
        """TC07: What is the university fee structure? -> Information unavailable"""
        data = self._ask("What is the university fee structure?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("unavailable" in answer or "not available" in answer or "administrative office" in answer)
        print(f"✓ TC07 Passed: {data['answer'][:70]}...")

    def test_TC08_greeting(self):
        """TC08: Hello, how are you? -> Friendly greeting"""
        data = self._ask("Hello, how are you?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("hello" in answer or "welcome" in answer or "campuscompass" in answer)
        print(f"✓ TC08 Passed: {data['answer'][:70]}...")

    def test_TC09_administration(self):
        """TC09: I need my academic records and certificates. -> Respective administrative office"""
        data = self._ask("I need my academic records and certificates.")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("administrative office" in answer or "administration" in answer)
        print(f"✓ TC09 Passed: {data['answer'][:70]}...")

    def test_TC10_weather_out_of_scope(self):
        """TC10: What is the weather today? -> Outside supplied campus knowledge base"""
        data = self._ask("What is the weather today?")
        self.assertTrue(data.get("success"))
        answer = data.get("answer", "").lower()
        self.assertTrue("outside" in answer or "unavailable" in answer or "campus" in answer)
        print(f"✓ TC10 Passed: {data['answer'][:70]}...")

    def test_paraphrased_queries(self):
        """Test paraphrased student expressions."""
        p1 = self._ask("I am struggling in my mathematics subject, who can help me?")
        self.assertIn("faculty advisor", p1.get("answer", "").lower())

        p2 = self._ask("Where do I go if water is leaking in my hostel room?")
        self.assertIn("hostel administration", p2.get("answer", "").lower())
        print("✓ Paraphrased Queries Passed")

    def test_follow_up_conversation(self):
        """Test multi-turn conversational context."""
        s_id = "multi-turn-test-session"
        t1 = self._ask("Can you tell me about campus placements?", session_id=s_id)
        self.assertIn("placement", t1.get("answer", "").lower())

        t2 = self._ask("And what about training for placements?", session_id=s_id)
        self.assertTrue("placement department" in t2.get("answer", "").lower() or "training" in t2.get("answer", "").lower())
        print("✓ Follow-up Context Passed")

if __name__ == "__main__":
    unittest.main()
