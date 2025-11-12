# agents/planner.py
from utils.database import get_topics_for_revision # <-- IMPORT DB FUNCTION
import json
import os

OUTPUT_PATH = "outputs/planner.json"

class PlannerAgent:
    """
    Generates a "smart" revision plan based on quiz performance
    (user progress), as per the Problem Statement.
    """
    def __init__(self):
        self.plan = []
        print("PlannerAgent (Smart): Initialized.")

    def generate_smart_plan(self):
        """
        Creates a revision plan by prioritizing the user's weakest topics.
        """
        print("PlannerAgent (Smart): Generating smart revision plan...")
        
        # Get weakest topics from the database
        weak_topics = get_topics_for_revision()
        
        if not weak_topics:
            print("PlannerAgent (Smart): No quiz data found. Generating simple plan.")
            self.plan = [{"topic_id": 0, "topic_preview": "Start by taking some quizzes!", "priority": "High", "total_incorrect": 0, "total_correct": 0}]
            self._save_plan()
            return self.plan

        plan = []
        for i, topic in enumerate(weak_topics):
            priority = "High" if i < 3 else ("Medium" if i < 7 else "Low")
            
            plan.append({
                "topic_id": topic['id'],
                "topic_preview": topic['content'][:100] + "...", # Show a preview
                "priority": priority,
                "total_incorrect": topic['total_incorrect'],
                "total_correct": topic['total_correct'],
                "last_revised": topic['last_revised']
            })
        
        self.plan = plan
        self._save_plan()
        print(f"PlannerAgent (Smart): Revision plan created with {len(self.plan)} prioritized items.")
        return self.plan

    def _save_plan(self):
        # We still save to JSON, just to display it in the UI
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            # Convert sqlite3.Row objects to dicts for JSON serialization
            json_plan = [dict(row) for row in self.plan]
            json.dump(json_plan, f, indent=2)