import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import db
from ui import App

if __name__ == "__main__":
    db.init_db()
    app = App()
    app.mainloop()
