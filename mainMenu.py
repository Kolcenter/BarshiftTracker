import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import random

version = "1.0"



# Function to read data from CSV file
def read_csv(file_path):
    data = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file, delimiter=';')
        for row in csv_reader:
            data.append(row)
    return data

# Function to write data to CSV file
def write_csv(file_path, data):
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        csv_writer.writerows(data)

# Function to sort data in CSV file alphabetically by name
def sort_csv_alphabetically(file_path):
    data = read_csv(file_path)
    sorted_data = sorted(data, key=lambda x: x[0].lower())  # Sort by name (case-insensitive)
    write_csv(file_path, sorted_data)

# Function to display data from CSV
def display_data():
    data = read_csv('people.csv')
    for row in data:
        tree.insert("", tk.END, values=row)

# Function to refresh the Treeview with updated data
def refresh_treeview():
    # Clear existing data in the Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Reload the updated data from people.csv
    display_data()

# Function to sort the Treeview by column
def sort_treeview(tree, col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    data.sort(reverse=reverse, key=lambda x: float(x[0]) if col == "Hours" else x[0].lower())
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))

# Function to save the schedule to a CSV file
def save_schedule(schedule_frame, barshift_data, selected_date):
    # Ask for confirmation
    if not messagebox.askyesno("Confirm Save", "Are you sure you want to save the schedule?"):
        return

    schedule = []
    for row_index, row in enumerate(barshift_data):
        timeslot = [row[0]]
        for col_index in range(1, int(row[1]) + 1):
            name_var = schedule_frame.grid_slaves(row=row_index, column=col_index)[0].get()
            timeslot.append(name_var)
        schedule.append(timeslot)

    # Construct the filename with the selected date
    filename = f'saved schedule {selected_date}.csv'

    with open(filename, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        csv_writer.writerows(schedule)

    # Show a popup message
    messagebox.showinfo("Success", "Schedule saved successfully")

# Function to load the schedule from a CSV file
def load_schedule(schedule_frame, barshift_data, selected_date):
    # Ask for confirmation
    if not messagebox.askyesno("Confirm Load", "Are you sure you want to load the schedule?"):
        return

    filename = f'saved schedule {selected_date}.csv'
    if os.path.exists(filename):
        saved_schedule = read_csv(filename)
        for row_index, row in enumerate(saved_schedule):
            for col_index in range(1, len(row)):
                name_var = schedule_frame.grid_slaves(row=row_index, column=col_index)[0]
                name_var.set(row[col_index])
    else:
        messagebox.showwarning("Error", "No existing schedule found")

# Function to register the schedule and update hours in people.csv
def register_schedule(schedule_frame, barshift_data):
    # Ask for confirmation
    if not messagebox.askyesno("Confirm Register", "Are you sure you want to register the schedule?"):
        return

    # Read the current people data
    people_data = read_csv('people.csv')
    people_dict = {row[0]: float(row[1]) for row in people_data}

    # Update hours based on the current schedule
    for row_index, row in enumerate(barshift_data):
        for col_index in range(1, int(row[1]) + 1):
            name_var = schedule_frame.grid_slaves(row=row_index, column=col_index)[0].get()
            if name_var and name_var in people_dict:
                people_dict[name_var] += 0.5

    # Write the updated people data back to the CSV
    updated_people_data = [[name, str(hours)] for name, hours in people_dict.items()]
    write_csv('people.csv', updated_people_data)

    # Refresh the Treeview with the updated data
    refresh_treeview()

    # Show a popup message
    messagebox.showinfo("Success", "Schedule registered successfully")

# Function to fill in the schedule with names
def pick_random_person(schedule_frame, barshift_data, random_person_label):
    # Read the current people data
    people_data = read_csv('people.csv')
    people_dict = {row[0]: float(row[1]) for row in people_data}

    # List of people already in the schedule
    existingNames = []

    # Sort people by hours (ascending)
    sorted_people = sorted(people_dict.items(), key=lambda x: x[1])

    # Check whose names are already in the schedule
    for row_index in range(len(barshift_data)):
        for col_index in range(1, int(barshift_data[row_index][1])+1):
            existingName = schedule_frame.grid_slaves(row=row_index, column=col_index)[0].get()
            if existingName and existingName not in existingNames:
                existingNames.append(existingName)

    # Remove entries with names in existingNames from sorted_people
    sorted_people = [person for person in sorted_people if person[0] not in existingNames]

    # Find a random person with the fewest hours
    min_hours = sorted_people[0][1]
    candidates = [person for person in sorted_people if person[1] == min_hours]
    selected_person = random.choice(candidates)
    random_person_label.config(text=selected_person[0]+" ("+str(selected_person[1])+" hours)")

def clear_schedule(schedule_frame):
    # Ask for confirmation
    if not messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the schedule?"):
        return

    # Clear all names in the schedule
    for widget in schedule_frame.winfo_children():
        if isinstance(widget, ttk.Combobox):
            widget.set("")



# Function to open the edit frame for the selected date
def open_edit_frame(edit_window, dates_listbox):
    selected_date = dates_listbox.get(dates_listbox.curselection())
    edit_window.destroy()

    edit_frame = tk.Toplevel(window)
    edit_frame.title(f"Editing barshift for {selected_date}")

    # Get the position of the main window
    main_window_x = window.winfo_x()
    main_window_y = window.winfo_y()
    main_window_width = window.winfo_width()

    # Set the position of the edit window near the "Edit barshift" button
    edit_frame.geometry(f"+{main_window_x + main_window_width + 10}+{main_window_y}")

    label = tk.Label(edit_frame, text=f"Editing barshift for {selected_date}")
    label.pack(pady=10)

    # Read the barshift standard data
    barshift_data = read_csv('barshiftStandard.csv')

    # Create a frame to hold the schedule
    schedule_frame = tk.Frame(edit_frame)
    schedule_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Predefined list of names (this can be replaced with actual data)
    names = [row[0] for row in read_csv('people.csv')]
    names.insert(0, "")  # Add an empty string option

    # Create the schedule table
    for row_index, row in enumerate(barshift_data):
        timeslot_label = tk.Label(schedule_frame, text=row[0])
        timeslot_label.grid(row=row_index, column=0, padx=1, pady=1)
        for col_index in range(1, int(row[1]) + 1):
            name_var = tk.StringVar()
            name_dropdown = ttk.Combobox(schedule_frame, textvariable=name_var, values=names)
            name_dropdown.grid(row=row_index, column=col_index, padx=1, pady=1)

    # Add the save schedule button
    save_button = tk.Button(edit_frame, text="Save", command=lambda: save_schedule(schedule_frame, barshift_data, selected_date))
    save_button.pack(side='left', pady=10, padx=5)

    # Add the load schedule button
    load_button = tk.Button(edit_frame, text="Load", command=lambda: load_schedule(schedule_frame, barshift_data, selected_date))
    load_button.pack(side='left', pady=10, padx=5)

    # Add the register schedule button
    register_button = tk.Button(edit_frame, text="Register", command=lambda: register_schedule(schedule_frame, barshift_data))
    register_button.pack(side='left', pady=10, padx=5)

    # Add the clear schedule button
    clear_button = tk.Button(edit_frame, text="Clear", command=lambda: clear_schedule(schedule_frame))
    clear_button.pack(side='left', pady=10, padx=5)

    # Add the person button and the random person label
    random_person_label = tk.Label(edit_frame, text="...")
    person_button = tk.Button(edit_frame, text="Person", command=lambda: pick_random_person(schedule_frame, barshift_data, random_person_label))

    person_button.pack(side='left', pady=10, padx=5)
    random_person_label.pack(side='left', pady=10, padx=5)

# Function to open the edit barshift window
def open_edit_barshift_window():
    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Barshift")

    # Get the position of the main window
    main_window_x = window.winfo_x()
    main_window_y = window.winfo_y()
    main_window_width = window.winfo_width()

    # Set the position of the edit window near the "Edit barshift" button
    edit_window.geometry(f"+{main_window_x + main_window_width + 10}+{main_window_y}")

    label = tk.Label(edit_window, text="Select a date to edit:")
    label.pack(pady=10)

    dates_listbox = tk.Listbox(edit_window)
    dates_listbox.pack(fill='both', expand=True, padx=10, pady=10)

    dates = read_csv('upcomingBarshifts.csv')
    for date in dates:
        dates_listbox.insert(tk.END, date[0])

    select_button = tk.Button(edit_window, text="Select", command=lambda: open_edit_frame(edit_window, dates_listbox))
    select_button.pack(pady=10)

def open_notes_window():
    notes_window = tk.Toplevel(window)
    notes_window.title("Edit Notes")

    # Get the position of the main window
    main_window_x = window.winfo_x()
    main_window_y = window.winfo_y()
    main_window_width = window.winfo_width()

    # Set the position of the notes window near the "Edit notes" button
    notes_window.geometry(f"+{main_window_x + main_window_width + 10}+{main_window_y}")
    
    # Function to save notes to CSV
    def save_notes(notes_data):
        write_csv('people_notes.csv', notes_data)
        messagebox.showinfo("Success", "Notes saved successfully")

    # Function to load notes from CSV
    def load_notes():
        return read_csv('people_notes.csv')

    # Function to add a new person
    def add_person():
        new_person = new_person_entry.get()
        if new_person:
            notes_data.append([new_person, ""])
            notes_listbox.insert(tk.END, new_person)
            new_person_entry.delete(0, tk.END)

    # Function to update the note for the selected person
    def update_note():
        selected_index = notes_listbox.curselection()
        if selected_index:
            selected_person = notes_listbox.get(selected_index)
            for row in notes_data:
                if row[0] == selected_person:
                    row[1] = note_text.get("1.0", tk.END).strip()
                    break

    # Load existing notes
    notes_data = load_notes()

    # Listbox to display names
    notes_listbox = tk.Listbox(notes_window)
    notes_listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    # Populate the listbox with names
    for row in notes_data:
        notes_listbox.insert(tk.END, row[0])

    # Text widget to edit notes
    note_text = tk.Text(notes_window, width=40, height=10)
    note_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    # Entry to add a new person
    new_person_entry = tk.Entry(notes_window)
    new_person_entry.pack(pady=5)

    # Button to add a new person
    add_person_button = tk.Button(notes_window, text="Add Person", command=add_person)
    add_person_button.pack(pady=5)

    # Button to save notes
    save_notes_button = tk.Button(notes_window, text="Save Notes", command=lambda: save_notes(notes_data))
    save_notes_button.pack(pady=5)

    # Button to update note
    update_note_button = tk.Button(notes_window, text="Update Note", command=update_note)
    update_note_button.pack(pady=5)

    # Function to display the note for the selected person
    def display_note_for_selected_person(event):
        selected_index = notes_listbox.curselection()
        if selected_index:
            selected_person = notes_listbox.get(selected_index)
            for row in notes_data:
                if row[0] == selected_person:
                    note_text.delete("1.0", tk.END)
                    note_text.insert(tk.END, row[1])
                    break

    # Bind the listbox selection event to display the note
    notes_listbox.bind("<<ListboxSelect>>", display_note_for_selected_person)


# Ensure people.csv is sorted alphabetically before any operations
sort_csv_alphabetically('people.csv')


# Main window
window = tk.Tk()
window.title("Bar Shift Tracker")

# Set the custom icon for the main window
window.iconbitmap('icon.ico')

# Set window size to half the surface area of a normal monitor (960x540)
window.geometry("540x540")

# Info frame (now the main frame)
info_frame = tk.Frame(window)
info_frame.pack(fill='both', expand=True)

# Label in info frame
label = tk.Label(info_frame, text="Barshift tool for Buitenwesten, version " + version)
label.pack(pady=20)

# Frame to contain the Treeview and the button
content_frame = tk.Frame(info_frame)
content_frame.pack(fill='both', expand=True, padx=15, pady=(10, 20))

# Treeview to display names and hours
tree = ttk.Treeview(content_frame, columns=("Name", "Hours"), show='headings')
tree.heading("Name", text="Name", command=lambda: sort_treeview(tree, "Name", False))
tree.heading("Hours", text="Hours", command=lambda: sort_treeview(tree, "Hours", False))

tree.pack(side='left', fill='both', expand=True)

# Button to propose barshift
propose_button = tk.Button(content_frame, text="Edit barshift", command=open_edit_barshift_window)
propose_button.pack(side='top', padx=10, pady=50)

# Button to edit notes
notes_button = tk.Button(content_frame, text="Edit notes", command=open_notes_window)
notes_button.pack(side='top', padx=10)




# Display data when the application starts
display_data()

# Start the GUI loop
window.mainloop()