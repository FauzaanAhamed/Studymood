class TaskRecommender:
    def suggest(self, mood, focus):
        if focus < 0.3:
            return "Take a 5-min break, stretch and relax."
        if mood == "sad":
            return "Do an easy/creative task to lift mood."
        if mood == "happy" and focus > 0.6:
            return "Great time for deep work (Pomodoro 25m)."
        return "Continue with medium tasks and stay consistent."
