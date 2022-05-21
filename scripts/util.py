def writeRows(path, rows):
    with open(path, 'w') as file:
        for row in rows:
            file.write('\t'.join([str(item) for item in row]) + "\n")
