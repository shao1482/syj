"""安全迁移脚本：为 Patient 表添加新字段，兼容已有数据"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "clinical.db")

NEW_COLUMNS = [
    ("patient_no", "TEXT DEFAULT ''"),
    ("inpatient_no", "TEXT DEFAULT ''"),
    ("bed_no", "TEXT DEFAULT ''"),
    ("department", "TEXT DEFAULT ''"),
    ("responsible_doctor", "TEXT DEFAULT ''"),
    ("responsible_nurse", "TEXT DEFAULT ''"),
    ("status", "TEXT DEFAULT '在院'"),
    ("risk_level", "TEXT DEFAULT NULL"),
]


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查看现有列
    cursor.execute("PRAGMA table_info(patients)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing_cols:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column already exists: {col_name}")

    # 将未设置状态的患者默认设为"在院"
    cursor.execute("UPDATE patients SET status = '在院' WHERE status IS NULL OR status = ''")
    conn.commit()
    conn.close()
    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()