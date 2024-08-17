import binascii

# Function to read the binary file and convert it to a hexadecimal string
def read_hallfame_file(filepath):
    with open(filepath, "rb") as file:
        content = file.read()
    return binascii.hexlify(content).decode('ascii')

# Function to save the modified data back to the HALLFAME file
def save_hallfame_file(filepath, hex_data):
    binary_data = binascii.unhexlify(hex_data)
    with open(filepath, "wb") as file:
        file.write(binary_data)

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

        # Save pilot information
        pilot_info = {
            "pilot_name": pilot_name,
            "total_score": total_score,
            "best_score": best_score,
            "rank": rank,
            "state_hex": state_hex  # Also save this for later restoration
        }
        pilot_data.append(pilot_info)
        
        if len(pilot_data) == 8:  # Stop after processing 8 pilots
            break
    
    # Extract the last two bytes of the file to keep them unchanged
    final_bytes = hex_dump[-4:]  # The last 2 bytes correspond to the last 4 hexadecimal characters
    
    return pilot_data, final_bytes

# Function to view and modify the pilot data
def edit_pilot_data(pilot_data):
    for index, pilot in enumerate(pilot_data):
        print(f"\nPilot {index + 1}:")
        print(f"Current Name: {pilot['pilot_name']}")
        new_name = input("New name (leave blank to keep current): ")
        if new_name:
            pilot['pilot_name'] = new_name
        
        print(f"Current Total Score: {pilot['total_score']}")
        new_total_score = input("New total score (leave blank to keep current): ")
        if new_total_score:
            pilot['total_score'] = int(new_total_score)
        
        print(f"Current Best Score: {pilot['best_score']}")
        new_best_score = input("New best score (leave blank to keep current): ")
        if new_best_score:
            pilot['best_score'] = int(new_best_score)
    
    return pilot_data

# Function to convert the modified data back to hexadecimal for saving
def convert_pilot_data_to_hex(pilot_data, final_bytes):
    hex_data = ""
    
    for pilot in pilot_data:
        try:
            # Build the record starting from the first two unchanged bytes
            record_hex = "0700"
            
            # Convert the name to hexadecimal, padding with zeros up to the 24th byte
            name_hex = binascii.hexlify(pilot['pilot_name'].encode('ascii')).decode('ascii')
            name_hex = name_hex.ljust(40, '0')  # Exactly 20 bytes (40 hexadecimal characters)
            record_hex += name_hex
            
            # Add padding to reach exactly the 25th byte
            padding_bytes = 24 - (len(record_hex) // 2)  # Calculate how many bytes are needed to reach the 25th byte
            record_hex += "00" * padding_bytes
            
            # Convert scores to hexadecimal (big-endian to little-endian)
            total_score_hex = f"{pilot['total_score']:08x}"  # 32-bit
            total_score_hex = total_score_hex[6:8] + total_score_hex[4:6] + total_score_hex[2:4] + total_score_hex[0:2]
            best_score_hex = f"{pilot['best_score']:04x}"  # 16-bit
            best_score_hex = best_score_hex[2:4] + best_score_hex[0:2]
            
            # Add the scores
            record_hex += total_score_hex + best_score_hex
            
            # Add the state (rank and medals) stored in "state_hex"
            record_hex += pilot["state_hex"]

            # Add final padding if necessary
            while len(record_hex) < 64:
                record_hex += "00"
            
            # Ensure the record is exactly 64 characters
            if len(record_hex) != 64:
                raise ValueError(f"Error: The record length is incorrect ({len(record_hex)} characters).")
        
        except Exception as e:
            print(f"Error creating the record for pilot {pilot['pilot_name']}: {e}")
            # Optionally, add recovery logic or fill with default values
            record_hex = record_hex.ljust(64, '0')  # Fills up to 64 characters in case of an error

        hex_data += record_hex
    
    # Add the final extra two bytes unchanged
    hex_data += final_bytes
    
    return hex_data

# Main function to run the editor
def main():
    file_path = "./HALLFAME"  # Point to the file in the same folder as the script
    hex_dump = read_hallfame_file(file_path)
    pilot_data, final_bytes = extract_and_convert_scores(hex_dump)
    
    print("Welcome to the HALLFAME editor!")
    modified_pilot_data = edit_pilot_data(pilot_data)
    
    try:
        hex_data_to_save = convert_pilot_data_to_hex(modified_pilot_data, final_bytes)
        save_hallfame_file(file_path, hex_data_to_save)
        print("Changes saved successfully!")
    except Exception as e:
        print(f"Error saving the file: {e}")
        # Attempt to save the file with partial data in case of an error
        try:
            save_hallfame_file(file_path, hex_data_to_save)
            print("File saved with partial data.")
        except:
            print("Unable to save the file, please restore the backup.")

if __name__ == "__main__":
    main()
