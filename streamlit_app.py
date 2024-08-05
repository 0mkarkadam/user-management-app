import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File to store user data
USER_DATA_FILE = 'user_data.csv'
CSS_FILE = 'styles.css'
UPLOADS_FILE = 'uploads.csv'

# Function to load CSS from file
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to load user data from CSV file
def load_user_data():
    try:
        return pd.read_csv(USER_DATA_FILE).to_dict(orient='records')
    except FileNotFoundError:
        return []

# Function to save user data to CSV file
def save_user_data(users):
    df = pd.DataFrame(users)
    df.to_csv(USER_DATA_FILE, index=False)

# Function to load upload data from CSV file
def load_upload_data():
    try:
        return pd.read_csv(UPLOADS_FILE).to_dict(orient='records')
    except FileNotFoundError:
        return []

# Function to save upload data to CSV file
def save_upload_data(uploads):
    df = pd.DataFrame(uploads)
    df.to_csv(UPLOADS_FILE, index=False)

# Function to add a new user
def add_user(username, email, password):
    new_user = {'Username': username, 'Email': email, 'Role': 'View Access', 'Password': password}
    st.session_state['users'].append(new_user)
    save_user_data(st.session_state['users'])

# Function to authenticate a user
def authenticate_user(identifier, password):
    for user in st.session_state['users']:
        if (user['Username'] == identifier or user['Email'] == identifier) and user['Password'] == password:
            return user
    return None

# Function to clear all user data (admin only)
def clear_user_data():
    if st.session_state['current_user']['Role'] == "Admin Access":
        st.session_state['users'] = []
        save_user_data(st.session_state['users'])
        st.success("All user data has been cleared.")
    else:
        st.error("Only users with Admin Access can clear data.")

# Initialize session state with user data from file
if 'users' not in st.session_state:
    st.session_state['users'] = load_user_data()

if 'uploads' not in st.session_state:
    st.session_state['uploads'] = load_upload_data()

# Load custom CSS
load_css(CSS_FILE)

# Logout Function
def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    st.session_state['current_page'] = "Login Page"

# Login Page
def login():
    st.markdown('<h1 class="main-title">Login Page</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Please Log In</p>', unsafe_allow_html=True)

    with st.form(key='login_form', clear_on_submit=True):
        identifier = st.text_input("Username or Email", placeholder="Enter username or email")
        password = st.text_input("Password", type='password', placeholder="Enter password")
        submit_button = st.form_submit_button("Login", help="Submit your login credentials")

        if submit_button:
            user = authenticate_user(identifier, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = user
                st.session_state['current_page'] = "User Management Console"
                st.session_state['users'] = load_user_data()
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username/email or password")

# Sign Up Page
def sign_up():
    st.markdown('<h1 class="main-title">Sign Up Page</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Create a new account</p>', unsafe_allow_html=True)

    with st.form(key='sign_up_form', clear_on_submit=True):
        username = st.text_input("Username", placeholder="Enter new username")
        email = st.text_input("Email", placeholder="Enter email address")
        password = st.text_input("Password", type='password', placeholder="Enter password")
        submit_button = st.form_submit_button("Sign Up", help="Create new user account")

        if submit_button:
            add_user(username, email, password)
            st.success(f"User '{username}' added with email '{email}'")
            st.session_state['users'] = load_user_data()  # Reload user data

# User Management Console Page
def user_management_console():
    st.markdown('<h1 class="main-title">User Management Console</h1>', unsafe_allow_html=True)

    st.sidebar.title("Filter by Role")
    roles = ["All"] + list(set(user['Role'] for user in st.session_state['users']))
    selected_role = st.sidebar.selectbox("Select a role", roles)

    if selected_role == "All":
        filtered_users = st.session_state['users']
    else:
        filtered_users = [user for user in st.session_state['users'] if user['Role'] == selected_role]

    st.write(f"### Users with {selected_role} role")
    # Hide password in the table
    users_df = pd.DataFrame(filtered_users).drop(columns=['Password'])
    st.dataframe(users_df)

    # Plotting charts
    df = pd.DataFrame(st.session_state['users'])
    if not df.empty:
        st.write("### User Role Distribution")
        fig, ax = plt.subplots()
        role_counts = df['Role'].value_counts()
        sns.barplot(x=role_counts.index, y=role_counts.values, ax=ax)
        ax.set_xlabel("Role")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of User Roles")
        st.pyplot(fig)

# Add User Page
def add_user_page():
    st.markdown('<h1 class="main-title">Add User</h1>', unsafe_allow_html=True)

    with st.form(key='add_user_form', clear_on_submit=True):
        username = st.text_input("Username", placeholder="Enter new username")
        email = st.text_input("Email", placeholder="Enter email address")
        role = st.selectbox("Role", ["View Access", "Edit Access", "Admin Access"])
        password = st.text_input("Password", type='password', placeholder="Enter password")
        submit_button = st.form_submit_button("Save User", help="Save the new user details")

        if submit_button:
            add_user(username, email, password)
            st.success(f"User '{username}' added with role '{role}' and email '{email}'")
            st.session_state['users'] = load_user_data()  # Reload user data

# Clear Data Page
def clear_data_page():
    st.markdown('<h1 class="main-title">Clear All Data</h1>', unsafe_allow_html=True)

    if st.button("Clear All User Data", help="This will delete all user data"):
        clear_user_data()
        st.session_state['users'] = load_user_data()  # Reload user data

# Upload Data Page
def upload_data_page():
    st.markdown('<h1 class="main-title">Upload Data</h1>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
            st.write(f"Filename: {uploaded_file.name}")
            st.write(bytes_data)
            st.session_state['uploads'].append({
                'Username': st.session_state['current_user']['Username'],
                'Filename': uploaded_file.name
            })
            save_upload_data(st.session_state['uploads'])

    if st.session_state['uploads']:
        st.markdown('<h2 class="sub-title">Uploaded Files</h2>', unsafe_allow_html=True)
        for upload in st.session_state['uploads']:
            st.markdown(f"<div class='file-details'>User: {upload['Username']}<br>File: {upload['Filename']}</div>", unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = "Login Page"

    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None

    if not st.session_state['logged_in']:
        menu = option_menu(
            menu_title=None,
            options=["Login", "Sign Up"],
            icons=["box-arrow-in-right", "person-plus"],
            menu_icon="menu-button",
            default_index=0,
            orientation="horizontal",
        )

        if menu == "Login":
            login()
        elif menu == "Sign Up":
            sign_up()
    else:
        # Menu Bar
        menu = option_menu(
            menu_title=None,
            options=["User Management Console", "Add User", "Clear Data", "Upload Data", "Logout"],
            icons=["list-task", "person-plus", "trash", "upload", "box-arrow-right"],
            menu_icon="menu-button",
            default_index=0,
            orientation="horizontal",
        )

        if menu == "User Management Console":
            user_management_console()
        elif menu == "Add User":
            add_user_page()
        elif menu == "Clear Data":
            clear_data_page()
        elif menu == "Upload Data":
            upload_data_page()
        elif menu == "Logout":
            logout()

if __name__ == '__main__':
    main()