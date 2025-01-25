import tkinter as tk
import pandas as pd

# Test pandas
print("Testing pandas...")
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df)

# Test tkinter
print("\nTesting tkinter...")
root = tk.Tk()
root.title("Test Window")
label = tk.Label(root, text="Test Label")
label.pack()
root.after(3000, root.destroy)  # Close after 3 seconds
root.mainloop()
