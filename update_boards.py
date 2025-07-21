
import pandas as pd
import requests

# ======= CONFIGURATION =======
EXCEL_FILE = "example_input.xlsx"  # Replace with your actual file path
ACCESS_TOKEN = "your_pinterest_access_token_here"
API_URL = "https://api.pinterest.com/v5/boards/"
MAX_CALLS = 1000  # API limit for trial access
# =============================

def update_board(board_id, title, description):
    """Send PATCH request to Pinterest API to update a board."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": title,
        "description": description
    }
    response = requests.patch(f"{API_URL}{board_id}", json=payload, headers=headers)
    return response.status_code, response.json()

def main():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"[ERROR] Failed to read Excel file: {e}")
        return

    count = 0
    with open("output_log.txt", "w", encoding="utf-8") as log:
        for _, row in df.iterrows():
            if count >= MAX_CALLS:
                log.write("Reached API limit. Halting further updates.\n")
                break
            board_id = row.get("board_id")
            title = row.get("title")
            description = row.get("description")
            if not board_id or not title:
                log.write(f"[SKIPPED] Missing required data in row: {row}\n")
                continue

            try:
                status, resp = update_board(board_id, title, description)
                if status == 200:
                    log.write(f"[SUCCESS] Board {board_id} updated.\n")
                elif status == 400 and "already exists" in str(resp).lower():
                    log.write(f"[DUPLICATE] Board name '{title}' already exists. Skipped.\n")
                else:
                    log.write(f"[FAIL] Board {board_id} error {status}: {resp}\n")
            except Exception as e:
                log.write(f"[ERROR] Request failed for {board_id}: {e}\n")
            count += 1

    print("Update complete. Check output_log.txt for results.")

if __name__ == "__main__":
    main()
