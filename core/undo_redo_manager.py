class Command:
    """
    Base para comandos de undo/redo.
    Cada comando debe implementar do() y undo().
    """
    def do(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

class UndoRedoManager:
    """
    Gestor de historial para deshacer y rehacer acciones.
    """
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def do(self, command: Command):
        command.do()
        self._undo_stack.append(command)
        self._redo_stack.clear()  # Al hacer una nueva acción, se borra la pila de redo

    def undo(self):
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.do()
        self._undo_stack.append(command)

    def can_undo(self):
        return bool(self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()