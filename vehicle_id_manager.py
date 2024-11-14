import json
import os

def save_vehicle_ids(tracked_ids, id_timestamps, filename):
    try:
        data = {'tracked_ids': list(tracked_ids), 'id_timestamps': id_timestamps}
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Vehicle IDs saved to {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Error saving vehicle IDs: {e}")

def load_vehicle_ids(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            tracked_ids = set(data.get('tracked_ids', []))
            id_timestamps = data.get('id_timestamps', {})
            id_timestamps = {int(k): v for k, v in id_timestamps.items()}
            print(f"Loaded {len(tracked_ids)} vehicle IDs from {os.path.abspath(filename)}")
            return tracked_ids, id_timestamps
        except Exception as e:
            print(f"Error loading vehicle IDs: {e}")
            return set(), {}
    else:
        print(f"No existing vehicle IDs found in {filename}.")
        return set(), {}

