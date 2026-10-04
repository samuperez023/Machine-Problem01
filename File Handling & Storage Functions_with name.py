import csv
from pathlib import Path


# Opens raw data
with open("raw_data.csv", mode="w", newline="") as raw:
    csv_writer = csv.writer(raw)
    csv_writer.writerow(["name", "date", "category", "amount", "desc"])

    while True:
        # Get user inputs
        user_name = input("Enter name: ")
        user_date = input("Enter date (YYYY-MM-DD): ")
        user_category = input("Enter category (e.g., Food, Transport): ")
        user_amount = input("Enter amount (in PHP): ")
        user_desc = input("Enter description (optional): ")

        # raw data
        raw_data = [user_name, user_date, user_category, user_amount, user_desc]
        csv_writer.writerow(raw_data)

        # Exit collting data loop
        while True:
            looper = input("Still enter values? (Yes/No): ").strip().lower()
            if looper in ("yes", "y", "no", "n"):
                break
            print("Invalid input, try again.")

        # End exit loop
        if looper in ("no", "n"):
            print("Done!")
            break


class File_Handling:
    HEADER = ["name", "date", "category", "amount", "desc"]
    PLACEHOLDER = ["N/A", "N/A", "N/A", "N/A", "N/A"]

    def parse_file_data(raw_data):
        with open(f"{raw_data}.csv", mode="r") as raw:
            csv_reader = csv.reader(raw)
            for line in csv_reader:
                print(line)

    def load_transactions_from_file(filename):

        path = Path(filename)
        # Accept either a folder path or a path to a file inside the folder
        folder = path if path.is_dir() else path.parent

        existing = [f.name for f in folder.glob("*.csv")]

        # Find the highest N among files named filename_N.csv
        highest = -1
        for name in existing:
            if name.startswith("filename_") and name.endswith(".csv"):
                number = name[len("filename_"):-len(".csv")]
                if number.isdigit() and int(number) > highest:
                    highest = int(number)

        # The ideal list: raw_data.csv plus filename_0 ... filename_highest
        ideal = ["raw_data.csv"]
        for num in range(highest + 1):
            ideal.append("filename_" + str(num) + ".csv")
        print("Ideal list:", ideal)

        # Create anything that's missing
        for name in ideal:
            if name not in existing:
                with open(folder / name, mode="w", newline="") as fold:
                    writer = csv.writer(fold)
                    writer.writerow(File_Handling.HEADER)
                    writer.writerow(File_Handling.PLACEHOLDER)
                print("created: " + name)

        # Open each file, make sure it has a header, and fill empty entries
        for name in ideal:
            # Read everything first, because we can't read and write the same file at once
            with open(folder / name, mode="r", newline="") as check:
                rows = list(csv.reader(check))

            # Check the first row: replace a bad header, or add one if there is none
            if not rows:
                rows.insert(0, File_Handling.HEADER)
                print("header added: " + name)
            elif rows[0] != File_Handling.HEADER:
                first = [cell.strip().lower() for cell in rows[0]]
                looks_like_header = False
                for cell in first:
                    if cell in File_Handling.HEADER:
                        looks_like_header = True

                if looks_like_header:
                    rows[0] = File_Handling.HEADER      # replace the bad header
                    print("header replaced: " + name)
                else:
                    rows.insert(0, File_Handling.HEADER)  # first row is data, keep it
                    print("header added: " + name)

            # Fill empty or missing entries in the data rows
            fixed = [File_Handling.HEADER]
            for row in rows[1:]:
                row = row + [""] * (len(File_Handling.HEADER) - len(row))  # pad short rows
                row = [cell if cell.strip() else "N/A" for cell in row]
                fixed.append(row)

            # Write the corrected rows back
            with open(folder / name, mode="w", newline="") as out:
                csv.writer(out).writerows(fixed)

    def save_transactions_to_file(transactions, filename):
        path = Path(filename)
        # Accept either a folder path or a path to a file inside the folder
        folder = path if path.is_dir() else path.parent

        # Find the highest N among files named filename_N.csv
        highest = -1
        for f in folder.glob("filename_*.csv"):
            number = f.name[len("filename_"):-len(".csv")]
            if number.isdigit() and int(number) > highest:
                highest = int(number)

        # The new file is one higher than the highest existing one
        new_name = "filename_" + str(highest + 1) + ".csv"

        with open(folder / new_name, mode="w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(File_Handling.HEADER)
            writer.writerows(transactions)

        print("saved: " + new_name)
        return new_name


# Example usage
example = "raw_data"
File_Handling.parse_file_data(example)

folder_path = r"C:\Users\Sam Perez\OneDrive\Desktop\new fiel"
File_Handling.load_transactions_from_file(folder_path)

# Read the transactions from raw_data.csv (skipping its header row)
with open(folder_path + r"\raw_data.csv", mode="r", newline="") as raw:
    reader = csv.reader(raw)
    next(reader, None)
    transactions = list(reader)

File_Handling.save_transactions_to_file(transactions, folder_path)