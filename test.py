import re

text = "Koşu Ayakkabısı araması için 12570 sonuç listeleniyor"

# Use regular expressions to find the number
match = re.search(r'\d+', text)

if match:
    number = match.group()
    print(number)
else:
    print("No number found in the text.")
