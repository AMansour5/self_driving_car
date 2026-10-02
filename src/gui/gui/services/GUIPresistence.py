class GUIPresistence:
    def __init__(self,index_path):
        self.index_path = index_path
        
    def getGUI(self):
        try:
            with open(self.index_path, 'r') as file:
                html_content = file.read()
                return html_content
        except Exception as e:
            print(f"Error occurred in GUI Presistence: {e}")