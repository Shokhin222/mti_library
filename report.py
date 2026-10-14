
from datetime import datetime
from pathlib import Path

class SessionReporter:
    def __init__(self, report_path: str | Path):
        self.report_path = Path(report_path)
        self.time_in = None

    def start(self):
        self.time_in = datetime.now()

    def finish(self, username: str):
        if self.time_in is None:
            return
        time_out = datetime.now()
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        new_file = not self.report_path.exists()
        with self.report_path.open("a", encoding="utf-8") as file:
            if new_file:
                file.write("+----------------------+---------------------+---------------------+\n")
                file.write("| login                | time_in             | time_out            |\n")
                file.write("+----------------------+---------------------+---------------------+\n")
            file.write(f"| {username[:20]:20} | {self.time_in:%Y-%m-%d %H:%M:%S} | {time_out:%Y-%m-%d %H:%M:%S} |\n")
            file.write("+----------------------+---------------------+---------------------+\n")
        self.time_in = None
