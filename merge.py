import csv

def merge_ieee_data(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        # 删除IEEE_Search_Index列
        fieldnames = [field for field in reader.fieldnames if field != 'IEEE_Search_Index']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()  # 写入表头

        for row in reader:
            # 如果abstract为空且IEEE_Search_Index不是"Not an IEEE article"，则将IEEE_Search_Index内容赋给abstract
            if row['abstract'] == "None" and row['IEEE_Search_Index'] != "Not an IEEE article":
                row['abstract'] = row['IEEE_Search_Index']
            # 删除IEEE_Search_Index列
            del row['IEEE_Search_Index']
            writer.writerow(row)

    print("Finished merging and cleaning data!")
