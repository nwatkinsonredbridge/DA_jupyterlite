import ipywidgets as widgets
from .functions import load_document, navigate_variables
from IPython.display import display, clear_output
from glob import glob 
from fuzzywuzzy import process
import os
import numpy as np

import pandas as pd

VAR_SELECTED = []
w_var = None
main_button = None
w_clean = None
w_status = None
status = None
w_log = None

company_name = None
L_var = []

loaded_data = None
loaded_company = None

#####################################

nav = navigate_variables()

#####################################

def update_choice(company, variables):
    global company_name
    global L_var
    company_name = company
    if isinstance(variables,str):
        L_var = [variables]
    else:    
        L_var = variables

def add_log_message(message):
    global w_log
    w_log.value += message +"\n"

#####################################

# UPDATE BUTTON


def on_button_clicked():
    global nav
    global VAR_SELECTED
    global company_name
    global L_var 

    global w_input1
    global w_input2
    company_name = w_input1.value
    varnames = w_input2.value
    L_var = varnames.split("|")
    L_var = list(np.unique([l for l in L_var if l != ""]))

    update_status("⏳ Loading...")

    if company_name is None:
        update_status("🔴 Error: Empty company name.")
        return

    out_status, dfile = load_document(company_name = company_name)

    if out_status == 1:
        for varn in L_var:
            if varn not in VAR_SELECTED:
                out_status = nav.select_var(varn)
                if out_status == 1:
                    VAR_SELECTED.append(varn)
                else:
                    add_log_message(f"### ERROR ###: {varn} not available.")
                    get_suggestion_varn(company_name, varn)

        w_var.options = VAR_SELECTED
        update_status(f"✅ Loaded\n{company_name.split("-")[0]}\n{company_name.split("-")[1].replace("_"," ")}")
        add_log_message(f"* File and variables loaded *")
    else:
        if company_name == "":
            update_status(f"🔴 Error: No company name provided\n")
            add_log_message(f"### Error ###: No company name provided.")
        else:
            update_status(f"🔴 Error: Not existing company name\n{company_name}")

            add_log_message(f"### ERROR ###: Company name: '{company_name}' not found.")
            if (company_name is not None) and (company_name != ""):
                get_suggestion()

#####################################

# STATUS

def update_status(message):
    global status
    with status:
        clear_output(wait=True)
        print(message)

def clean_up():
    global VAR_SELECTED
    global nav
    for varn in VAR_SELECTED:
        nav.undo_highlight(varn)
    VAR_SELECTED = []
    w_var.options = VAR_SELECTED

def clear_log(b):
    w_log.value = ""

#####################################

# MAIN FUNCTION

def prepare_widget():
    global w_var
    global main_button
    global w_clean
    global w_status
    global status
    #
    global company_name
    global L_var
    global w_input1
    global w_input2
    global w_log

    # Update html: HOW TO UPDATE IF IN ANOTHER FILE -> NEED EXTRA FUNCTION
    button = widgets.Button(description = "UPDATE", layout = widgets.Layout(width = "20%"))
    load_document(company_name = None)
    button.on_click(lambda x: on_button_clicked())
    main_button = button

    # VARIABLE DROPDOWN, NEED TO BE UPDATED WHEN BUTTON OR CLEAN UP
    variable_dropdown = widgets.Dropdown(
        options=[],
        description='SELECTED:',
        layout = widgets.Layout(width = "20%"))
    w_var = variable_dropdown

    # CLEAN UP: unselect variables
    clean_up_button = widgets.Button(description="CLEAN UP", button_style='danger', layout = widgets.Layout(width = "20%"))
    clean_up_button.on_click(lambda x: clean_up())
    # Here function on button click apply nav.undo_highlight(Lvar)
    w_clean = clean_up_button

    # STATUS: to display
    status_display = widgets.Output()
    status_box = widgets.Box([status_display], layout=widgets.Layout(
        border='1px solid black', 
        padding='2px',
        width = "40%",
    ))
    status  = status_display
    w_status = status_box
    button_box = widgets.HBox([button, clean_up_button, variable_dropdown, status_box], layout=widgets.Layout(width='100%'))

    #############################

    input1 = widgets.Text(placeholder='FR0000121329-THALES', layout=widgets.Layout(width='50%'))
    w_input1 = input1
    #
    input2 = widgets.Text(placeholder='ifrs-full:Assets|ifrs-full:ProfitLoss', layout=widgets.Layout(width='50%'))
    w_input2 = input2

    #

    label1 = widgets.Label(value="Company:")
    label2 = widgets.Label(value="Variable name(s):")
    label1.layout = widgets.Layout(width=input1.layout.width)
    label2.layout = widgets.Layout(width=input2.layout.width)

    input_label_box = widgets.HBox([label1, label2], layout=widgets.Layout(width='100%'))
    input_box = widgets.HBox([input1, input2], layout=widgets.Layout(width='100%'))

    #############################
    #### LOG

    log_area = widgets.Textarea(
        value='Log output:\n',
        layout=widgets.Layout(width='100%', height='150px'),  # Fixed width and height
        disabled=True , # Make the text area read-only
        border='1px solid black'
    )
    log_area.layout.overflow = 'scroll'
    log_area.style = {'color': 'black'}
    w_log = log_area

    # Create a button to clear the log
    clear_log_button = widgets.Button(description="Clear Log", button_style='warning')
    clear_log_button.on_click(clear_log)

    log_box = widgets.HBox([log_area, clear_log_button],  layout=widgets.Layout(width='100%'))
    layout = widgets.VBox([input_label_box, input_box, button_box, log_box])
    
    #
    
    update_status("⚪️ Initialized.")
    display(layout)

#############################################

# SUGGESTIONS 

current_directory = os.path.dirname(os.path.abspath(__file__))
df_ref = pd.read_excel(f"{current_directory}/EXPORT_2023/COMPANY_REFERENCES.xlsx")
d = glob(f"{current_directory}/../EXPORT_2023/RAW_CLEANUP/*/")
L_companies = [dd.split("/")[-2] for dd in d]
threshold = 80


def get_suggestion():
    global company_name

    top_matches = process.extract(company_name, L_companies, limit=10)
    filtered_matches = [match for match in top_matches if match[1] >= threshold]

    if len(filtered_matches) == 0:
        add_log_message("-> No suggestion for company")
    else:
        add_log_message("-> Suggestion for company")
        for match in filtered_matches:
            add_log_message(f"   - {match[0]}")

def get_suggestion_varn(company, varn):
    global loaded_company
    global loaded_data

    if loaded_company != company:
        out = df_ref[df_ref["REF"] == company_name]["EXPORT_NAME"].iloc[0]
        df_tmp = pd.read_excel(f"EXPORT_2023/EXTRACTED/{out}_output.xlsx")
        loaded_data = list(df_tmp["concept_name"].unique())
        loaded_company = company
    
    top_matches = process.extract(varn, loaded_data, limit=10)
    filtered_matches = [match for match in top_matches if match[1] >= threshold]

    if len(filtered_matches) == 0:
        add_log_message(f"-> No suggestion for variable: {varn}")
    else:
        add_log_message(f"-> Suggestion for variable: {varn}")
        for match in filtered_matches:
            add_log_message(f"   - {match[0]}")