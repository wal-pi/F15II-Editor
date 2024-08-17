import binascii

# Function to read the binary file and convert it to a hexadecimal string
def read_hallfame_file(filepath):
    with open(filepath, "rb") as file:
        content = file.read()
    return binascii.hexlify(content).decode('ascii')

# Function to extract and convert pilot data
def extract_and_convert_scores(hex_dump):
    record_size = 64  # Each record is 32 bytes, so 64 hexadecimal characters
    pilot_data = []
    
    for i in range(0, min(len(hex_dump) - 4, record_size * 8), record_size):  # Consider only 8 pilots
        record_hex = hex_dump[i:i + record_size]
        
        # Extract pilot name (from the 3rd to the 24th byte = 40 hexadecimal characters)
        name_hex = record_hex[4:44]
        pilot_name = bytes.fromhex(name_hex).decode('ascii', 'ignore').split('\x00', 1)[0]
        
        # Extract and convert total score (positions 24-27)
        total_score_hex = record_hex[48:56]
        big_endian_total = total_score_hex[6:8] + total_score_hex[4:6] + total_score_hex[2:4] + total_score_hex[0:2]
        total_score = int(big_endian_total, 16)
        
        # Extract and convert best score (positions 28-29)
        best_score_hex = record_hex[56:60]
        big_endian_best = best_score_hex[2:4] + best_score_hex[0:2]
        best_score = int(big_endian_best, 16)
        
        # Extract medals and rank (positions 31-32)
        state_hex = record_hex[60:64]
        state_byte = int(state_hex, 16)
        rank_value = state_byte & 0x07  # The 3 least significant bits of byte 31
        
        # Rank mapping
        rank_map = {
            6: "General",
            5: "Colonel",
            4: "Lt Colonel",
            3: "Major",
            2: "Captain",
            1: "1st Lt",
            0: "2nd Lt"
        }
        rank = rank_map.get(rank_value, "Unknown")

        # Medals mapping
        medals = []
        if state_byte & 0x10:
            medals.append("Air Force Achievement Medal")
        if state_byte & 0x08:
            medals.append("Air Force Commendation Medal")
        if state_byte & 0x04:
            medals.append("Silver Star")
        if state_byte & 0x02:
            medals.append("Distinguished Flying Cross")
        if state_byte & 0x01:
            medals.append("Air Force Cross")
        
        # Save pilot information
        pilot_info = {
            "pilot_name": pilot_name,
            "total_score": total_score,
            "best_score": best_score,
            "rank": rank,
            "medals": medals
        }
        pilot_data.append(pilot_info)
        
        if len(pilot_data) == 8:  # Stop after processing 8 pilots
            break
    
    return pilot_data

# Function to display pilot data
def display_pilot_data(pilot_data):
    for index, pilot in enumerate(pilot_data):
        print(f"\nPilot {index + 1}:")
        print(f"Name: {pilot['pilot_name']}")
        print(f"Total Score: {pilot['total_score']}")
        print(f"Best Score: {pilot['best_score']}")
        print(f"Rank: {pilot['rank']}")
        print(f"Medals: {', '.join(pilot['medals']) if pilot['medals'] else 'None'}")

# Main function to execute the viewer
def main():
    file_path = "./HALLFAME"  # Point to the file in the same folder as the script
    hex_dump = read_hallfame_file(file_path)
    pilot_data = extract_and_convert_scores(hex_dump)
    
    print("HallFame Viewer")
    display_pilot_data(pilot_data)

if __name__ == "__main__":
    main()
