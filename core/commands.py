from struktix.core.undo_redo_manager import Command

class AddNodeCommand(Command):
    def __init__(self, project, node):
        self.project = project
        self.node = node

    def do(self):
        self.project.add_node(self.node)

    def undo(self):
        self.project.remove_node(self.node)