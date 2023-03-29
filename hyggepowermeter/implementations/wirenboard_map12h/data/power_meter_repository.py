import sqlite3

from hyggepowermeter.hygge_logging.hygge_logging import logger
from hyggepowermeter.implementations.wirenboard_map12h.registers import REGISTER_CONFIGS


class Map12Repository:
    def __init__(self, db):
        self.db = db + ".db"
        self.__create_table()

    def __create_table(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Generate columns definition based on the register configurations
        column_definitions = [f"{config[2]} REAL" for config in REGISTER_CONFIGS]

        # Add additional columns to the column_definitions list if needed
        column_definitions.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")
        column_definitions.insert(1, "device_id INTEGER")
        column_definitions.insert(2, "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")

        # Create the table
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS meter_readings (
                            {', '.join(column_definitions)}
                            )''')
        logger.debug(f"Table created")
        conn.close()

    def save(self, readings, device_id):
        conn = sqlite3.connect(self.db)
        readings['device_id'] = device_id
        columns = ', '.join(readings.keys())
        placeholders = ', '.join('?' * len(readings))
        sql = f"INSERT INTO meter_readings ({columns}) VALUES ({placeholders})"
        cursor = conn.cursor()
        cursor.execute(sql, tuple(readings.values()))
        conn.commit()
        conn.close()
        logger.debug(f"Registers stored in local db")

    def read_all_values(self, device_id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM meter_readings WHERE device_id = ?', (device_id,))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
