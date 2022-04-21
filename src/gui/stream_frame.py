class StreamFrame:

    def __init__(self, container_frame):
        self.container_frame = container_frame
        self.stream_frame = None

    def create_frame(self, tk=None):
        self.stream_frame = tk.Frame(self.container_frame)
        self.stream_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
