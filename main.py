# Main file of the script runner program
import configparser
import mariadb
import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator

# read the .ini configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# get the database informations
db_host = config['DATABASE']['HOST']
db_port = config['DATABASE']['PORT']
db_user = config['DATABASE']['USER']
db_password = config['DATABASE']['PASSWORD']
db_name = config['DATABASE']['DATABASE']

# get the script folder
script_folder = config['SCRIPTS']['PATH']

# connect to the database
try:
	conn = mariadb.connect(
		user=db_user,
		password=db_password,
		host=db_host,
		port=int(db_port),
		database=db_name
	)
except mariadb.Error as e:
	print(f"Error connecting to MariaDB Platform: {e}")
	sys.exit(1)

# get the cursor
cur = conn.cursor()

# get the script list
script_list = os.listdir(script_folder)

print("Script runner started")
print("Script list:")
print(script_list)

def save_script():
	# get the current file name
	current_file = file_label.cget("text")
	
	# check if a file is opened
	if current_file == "No file opened":
		result.delete(1.0, tk.END)
		result.insert(tk.END, "No script to save")
		return
	
	# get the script content
	script_content = text.get(1.0, tk.END)
	
	# save the script content to the file
	with open(os.path.join(script_folder, current_file), "w") as file:
		file.write(script_content)
	result.delete(1.0, tk.END)
	result.insert(tk.END, "Script saved successfully")

# create the main window
# left part is the script list
# right part is the script content on top and the result on bottom
root = tk.Tk()
root.title("Script Runner")
root.geometry("800x600")
root.style = ttk.Style()

# create the left frame
frame_left = ttk.Frame(root, padding="10 10 10 10")
frame_left.pack(side=tk.LEFT, fill=tk.Y)

# create the right frame
frame_right = ttk.Frame(root, padding="10 10 10 10")
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# create the script content
file_label = ttk.Label(frame_right, text="No file opened")
file_label.pack(pady=5)
text = tk.Text(frame_right, height=20, width=80, wrap=tk.WORD, relief=tk.SUNKEN, borderwidth=1)
text.pack(pady=5, fill=tk.BOTH, expand=True)

# save button
save_button = ttk.Button(frame_right, text="Save", command=save_script)
save_button.pack(pady=5)

# Add syntax highlighting to the text widget
percolator = Percolator(text)
color_delegator = ColorDelegator()
percolator.insertfilter(color_delegator)

# create the result content
result = tk.Text(frame_right, height=10, width=80, wrap=tk.WORD, relief=tk.SUNKEN, borderwidth=1)
result.pack(pady=5, fill=tk.BOTH, expand=True)

def display_script_content(event):
	# get the selected script
	selected_script = listbox.get(listbox.curselection())
	
	# open the script file
	with open(script_folder + "/" + selected_script, "r") as file:
		script_content = file.read()
	
	# display the script content
	file_label.config(text=selected_script)
	text.delete(1.0, tk.END)
	text.insert(tk.END, script_content)
 
def run_script():
	# get the script content
	script_content = text.get(1.0, tk.END)
	
	# execute the script
	try:
		cur.execute(script_content)
		conn.commit()
		result.delete(1.0, tk.END)
		
		# fetch the result if it's a SELECT query
		if cur.description:
			rows = cur.fetchall()
			for row in rows:
				result.insert(tk.END, f"{row}\n")
		else:
			result.insert(tk.END, "Script executed successfully")
	except mariadb.Error as e:
		result.delete(1.0, tk.END)
		result.insert(tk.END, f"Error: {e}")
  
def open_folder():
	global script_folder, script_list
	script_folder = filedialog.askdirectory()
	script_list = os.listdir(script_folder)
	listbox.delete(0, tk.END)
	for script in script_list:
		listbox.insert(tk.END, script)

def open_file():
	file_path = filedialog.askopenfilename()
	if file_path:
		with open(file_path, "r") as file:
			script_content = file.read()
		file_label.config(text=os.path.basename(file_path))
		text.delete(1.0, tk.END)
		text.insert(tk.END, script_content)

def create_new_script():
	# ask for the new script name
	new_script_name = tk.simpledialog.askstring("New Script", "Enter script name:")
	
	# check if a name was provided
	if new_script_name:
		# add .sql extension if not present
		if not new_script_name.endswith(".sql"):
			new_script_name += ".sql"
		
		# create the new script file
		new_script_path = os.path.join(script_folder, new_script_name)
		with open(new_script_path, "w") as file:
			file.write("")
		
		# update the script list
		script_list.append(new_script_name)
		listbox.insert(tk.END, new_script_name)
		file_label.config(text=new_script_name)
		text.delete(1.0, tk.END)
		result.delete(1.0, tk.END)
		result.insert(tk.END, "New script created successfully")

# create the script list
listbox = tk.Listbox(frame_left, height=28, width=20, relief=tk.SUNKEN, borderwidth=1)
for script in script_list:
	listbox.insert(tk.END, script)
listbox.pack(pady=5, fill=tk.Y, expand=True)

# on click on a script, display the script content
listbox.bind("<<ListboxSelect>>", display_script_content)

# run button
run_button = ttk.Button(frame_left, text="Run", command=run_script)
run_button.pack(pady=5)

# new button
new_button = ttk.Button(frame_left, text="New", command=create_new_script)
new_button.pack(pady=5)

# file > open folder (script folder)
# file > open file (script file)
# add menu here
# create a menu bar
menu_bar = tk.Menu(root)

# create a file menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Folder", command=open_folder)
file_menu.add_command(label="Open File", command=open_file)

# add the file menu to the menu bar
menu_bar.add_cascade(label="File", menu=file_menu)

# display the menu bar
root.config(menu=menu_bar)

# start the main loop
root.mainloop()