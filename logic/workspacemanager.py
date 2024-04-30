class WorkspaceManager:
    _instances=[]
    def rebuild_all()->None:
        for h in WorkspaceManager._instances:
            h.rebuild()
