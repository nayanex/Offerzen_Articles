from src.automation.service_layer import get_workflows_by_status

class AutomationFramework:
    def __init__(self, status):
        self.status = status
        
    def run(self):
        get_workflows_by_status(self.status)

if __name__ == "__main__":
    automation = AutomationFramework("FINISHED")
    automation.run()