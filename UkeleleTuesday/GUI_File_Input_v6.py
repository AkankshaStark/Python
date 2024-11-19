import tkinter as tk
from tkinter import filedialog # Makes it possible to open files on the user computer
from PIL import Image, ImageTk  # Makes it possible to open, resize and manipulate images

class InputGUI:
    def __init__(self, master):
        self.master = master  # Save master reference where all of the GUI is saved

        # Set the background color of the entire window to white
        master.configure(bg='#FFFFFF')

        # Add logo and title frame at the top
        self.logo_frame = tk.Frame(master, bg='#FFFFFF')
        self.logo_frame.pack(side="top", anchor="w", padx=10, pady=10)

        # Add the Ukulele Tuesday Logo
        pil_logo_image = Image.open(r"C:\Users\rebec\OneDrive\Documentos\UCD First Trimester\Programming for Analytics\group assignment\ukelele_tuesday_logo.png")
        resized_logo_image = pil_logo_image.resize((80, 80), Image.Resampling.LANCZOS)  
        logo_image = ImageTk.PhotoImage(resized_logo_image)
        logo_label = tk.Label(self.logo_frame, image=logo_image, bg='#FFFFFF')
        logo_label.image = logo_image  # Keep a reference
        logo_label.pack(side="left", padx=10)

        # Add title next to the logo
        title_label = tk.Label(
            self.logo_frame,
            text="Ukulele Tuesday",
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side="left", padx=10)

        #Main Content of the page
        # Create a main frame to hold all content except the proceed button
        self.main_frame = tk.Frame(master, bg='#FFFFFF')
        self.main_frame.pack(fill='both', expand=True) #allows the frame and its content to resize according to the users pc

        # Dictionary to store selected file paths
        self.file_paths = {}

        # Creating upload sections
        self.create_file_upload_section("Tabdb", 0)
        self.create_file_upload_section("Playdb", 1)
        self.create_file_upload_section("Requestdb", 2)

        # Style the proceed button and pack it at the bottom right
        self.proceed_button = tk.Button(
            master,
            text="Proceed",
            command=self.next_window,
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 12),
            bd=1,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#8B4513',
            padx=20,
            pady=10
        )
        self.proceed_button.pack(side="bottom", anchor="e", padx=20, pady=20)

    def create_file_upload_section(self, db_name, section_number):
        """Creates a file upload section with labels and a button."""
        
        # Outer frame acting as a border
        border_frame = tk.Frame(
            self.main_frame,
            bg='#FFFFFF',
            highlightbackground='#E0E0E0',  # Subtle border color
            highlightthickness=1
        )
        border_frame.grid(
            row=section_number,
            column=0,
            padx=20,
            pady=10,
            sticky='w'
        )

        # Inner frame adds spacing within the border frame
        inner_frame = tk.Frame(border_frame, bg='#FFFFFF')
        inner_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Title label aka Section Header
        title_label = tk.Label(
            inner_frame,
            text=f"Upload File - {db_name}",
            bg='#FFFFFF',
            fg='#c49526',
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, sticky='w')

        # Upload icon image for Browse Button
        pil_upload_icon = Image.open(r"C:\Users\rebec\OneDrive\Documentos\UCD First Trimester\Programming for Analytics\group assignment\upload.png")
        resized_upload_icon = pil_upload_icon.resize((40, 40), Image.Resampling.LANCZOS)  # Resize icon
        upload_icon = ImageTk.PhotoImage(resized_upload_icon)
        browse_button = tk.Button(
            inner_frame,
            image=upload_icon,
            command=lambda: self.browse_file(db_name),
            bg='#FFFFFF',
            borderwidth=0,  # Remove the button border
            highlightthickness=0,  # Remove highlight
            activebackground='#FFFFFF'
        )
        browse_button.image = upload_icon  # Keep a reference
        browse_button.grid(row=0, column=1, sticky='e', padx=10)

        # Description label
        status_label = tk.Label(
            inner_frame,
            text="Upload a CSV file from your device",
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 14),
            wraplength=500  # Adjust for better alignment
        )
        status_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))

        # Store the status label for updating later
        self.file_paths[db_name] = {'path': None, 'label': status_label}

    def browse_file(self, db_name):
        """Opens a file dialog to select a CSV file on the user machine and stores the path."""

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title=f"Select CSV file for {db_name}",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )

        if file_path:
            # Store the selected file path
            self.file_paths[db_name]['path'] = file_path

            # Update the label to show the selected file
            self.file_paths[db_name]['label'].config(text=f"Selected file: {file_path}")

    #Next window with only a small message as a placeholder
    def next_window(self):
        """Create the next window."""
        next_window = tk.Toplevel(self.master)
        next_window.title("Data Filters")

        # Set background color of the new window to white
        next_window.configure(bg='#FFFFFF')

        label = tk.Label(
            next_window,
            text="Go ahead and query the data and generate plots, go wild!",
            bg='#FFFFFF',
            font=('Arial', 14)
        )
        label.pack()

# Main application setup
root = tk.Tk()
root.geometry("600x500")  # Adjust window size as needed
root.title("Ukulele Tuesday")

InputGUI(root)
root.mainloop()
