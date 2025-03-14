# JSF

## Introduction

This Django project is designed for [provide a brief description of the project]. It consists of several Django apps, each serving a specific purpose. Below are the apps along with their functionalities.

## Project Structure

## Main App

The `mainapp` in this Django project serves as the main application responsible for managing and displaying various app links accessible to users based on their permissions. Below is an outline of the components and functionalities within this app:

### Models

#### `AppLink` Model

- **Fields:**
  - Name (CharField, unique)
  - URL (CharField)
  - Description (TextField, optional)
  - Visible (BooleanField, default: True)
  - Required Permission (CharField, max_length: 255, help_text: "Permission required to access this app")

- **Methods:**
  - `__str__(self)`: Returns the name of the app link.

### Admin Interface

- Customized admin interface is provided for efficient management.
- `AppLinkAdmin` class is registered to facilitate admin operations.
- Various fields are displayed in the admin interface, and `visible` field is editable directly from the list view.

### Permissions

- A custom permission `use_JSF` is defined, allowing users to access specific apps.

### URL Configuration (`mainapp/urls.py`)

- A single URL pattern is defined:
  - `'``'` (Empty): Maps to the `landing_page` view, which serves as the landing page for displaying available app links.

### Views (`mainapp/views.py`)

#### `landing_page` View

- Requires user authentication (login_required).
- Fetches all visible `AppLink` instances.
- Filters app links based on the user's permissions.
- Displays a warning message if the user does not have permission to access any apps.
- Renders the `landing_page.html` template with the filtered app links.

### How to Use

1. **Access Landing Page:**

    - Navigate to the root URL [http://localhost:8000/](http://localhost:8000/) after running the development server to access the landing page and view available app links.

### Permissions

- Users must have the `use_JSF` permission to access specific apps.


## Oracle Query App

The `oraclequery` app in this Django project handles the execution and management of Oracle queries. It provides a user interface for executing saved queries and displaying results. Below is an outline of the components and functionalities within this app:

### Models

#### `SavedQuery` Model

- **Fields:**
  - Name (CharField)
  - Query (TextField)
  - Variables (TextField, JSON representation)
  - Query Type (CharField, choices: 'impax', 'ei', default: 'impax')

- **Methods:**
  - `__str__(self)`: Returns the name of the saved query.

#### `FriendlyDBName` Model

- **Fields:**
  - DB Alias (CharField, unique)
  - Friendly Name (CharField)

- **Methods:**
  - `__str__(self)`: Returns a formatted string with the friendly name and DB alias.

### Admin Interface

- `SavedQuery` and `FriendlyDBName` models are registered in the admin interface.
- Provides an organized view for efficient management of saved queries and friendly database names.

### Permissions

- Custom permissions `use_oracle_queries` are defined to control access to Oracle queries.

### URL Configuration (`oraclequery/urls.py`)

- Two URL patterns are defined:
  - `'``'` (Empty): Maps to the `main_page` view, displaying a list of available queries.
  - `'<int:query_id>/'`: Maps to the `execute_query_view` view, allowing the execution of a specific query.

### Views (`oraclequery/views.py`)

#### `main_page` View

- Requires user authentication (login_required).
- Fetches all saved queries.
- Retrieves friendly names of database aliases.
- Renders the `oraclequery_main_page.html` template with queries and associated servers.

#### `execute_query_view` View

- Requires `use_oracle_queries` permission.
- Executes a specific saved query and displays results.
- Supports user-inputted variables and human-readable date parameters.

#### `execute_query` View

- Requires `use_oracle_queries` permission.
- Fetches data for a query using parameters from the request.
- Returns results in JSON format.

#### `fetch_data` Function

- Fetches data for a query and server combination.
- Utilized by the `execute_query` view.

### How to Use

1. **Access Main Page:**

    - Navigate to the Oracle Query app's main page by visiting [http://localhost:8000/oraclequery/](http://localhost:8000/oraclequery/).

2. **Execute a Query:**

    - Click on a specific query to execute it and view results.

3. **Permissions:**

    - Users must have the `use_oracle_queries` permission to execute and view Oracle queries.


## Server Logs App

The `serverlogs` app in this Django project manages and searches through server logs stored on remote servers. It now supports logs from both remote **Windows** and **Linux** servers. The app connects to these servers, retrieves logs, and allows you to perform searches across them.

---

### Models

#### `PACSCore` Model

- **Fields:**
  - **Name:** (CharField, unique)
  - **Description:** (TextField)
  - **Server Type:** (CharField with choices)  
    Allows you to select whether the associated servers are **Windows** or **Linux**.

- **Methods:**
  - `__str__(self)`: Returns the name of the PACS core.

#### `RemoteWindowsServer` Model

- **Fields:**
  - **Core:** (ForeignKey to `PACSCore`)
  - **Name:** (CharField)
  - **IP Address:** (GenericIPAddressField)
  - **Credentials:** (EncryptedCharField)
  - **Logs Folder:** (CharField)

- **Methods:**
  - `__str__(self)`: Returns a formatted string with the server name and associated PACS core.

#### `RemoteLinuxServer` Model

- **Fields:**
  - **Core:** (ForeignKey to `PACSCore`)
  - **Name:** (CharField)
  - **IP Address:** (GenericIPAddressField)
  - **SSH Username:** (CharField)
  - **SSH Key Path:** (CharField)  
    Specifies the file path to the SSH private key. A default key location is provided.
  - **Logs Folder:** (CharField)

- **Methods:**
  - `__str__(self)`: Returns a formatted string with the server name and associated PACS core.

#### `PredefinedSearch` Model

- **Fields:**
  - **Name:** (CharField)
  - **Search Query:** (TextField)

- **Methods:**
  - `__str__(self)`: Returns the name of the predefined search.

---

### Admin Interface

- The models `PACSCore`, `RemoteWindowsServer`, `RemoteLinuxServer`, and `PredefinedSearch` are registered in the Django admin.
- This provides an organized interface for efficient management of PACS cores, remote servers (both Windows and Linux), and predefined searches.
- The `PACSCore` model's **Server Type** field ensures that only one type of server (Windows or Linux) is selected per PACS core.

---

### Permissions

- A custom permission `use_serverLogs` is defined to control access to server logs.

---

### URL Configuration (`serverlogs/urls.py`)

- Two URL patterns are defined:
  - `''` (Empty): Maps to the `search_logs` view, which displays the search page.
  - `'execute/'`: Maps to the `execute_search` view, which executes the log search.

---

### Views (`serverlogs/views.py`)

#### `search_logs` View

- **Access:** Requires the `use_serverLogs` permission.
- **Functionality:**
  - Fetches all PACS cores and predefined searches.
  - Renders the `search_logs.html` template with available options.

#### `execute_search` View

- **Access:** Requires the `use_serverLogs` permission.
- **Functionality:**
  - Executes a search on the selected PACS core using either a predefined search or free text.
  - **Server-Specific Processing:**  
    - For **Linux** PACS cores, it uses an SSH/SFTP-based function that authenticates via key-based authentication (using a default or specified key file).
    - For **Windows** PACS cores, it uses the existing SMB-based function.
  - Processes server logs in parallel and retrieves the search results.

---

### Log Processing Functions

- **Common Functions:**
  - `extract_log_details(log_message)`: Extracts details such as reason, calling AE, and called AE from a log message.
  - `extract_and_convert_timestamp(timestamp_line)`: Extracts and converts a timestamp from a log file line.
- **Windows Server Functions:**
  - `process_log_file(log_file_path, search_pattern, results_list, is_specific_search=False)`: Processes a Windows log file for a given search pattern.
  - `process_server(server, search_pattern, results_list, is_specific_search=False)`: Processes logs from a Windows server.
- **Linux Server Functions:**
  - `process_server_linux(server, search_pattern, results_list, is_specific_search=False)`:  
    Uses Paramiko to connect via SSH using key-based authentication (with a default key file if none is provided) and processes logs from a Linux server.
  - Uses the `posixpath` module to construct Linux file paths properly.

---

### How to Use

1. **Search Logs:**

   - Navigate to the Server Logs app by visiting [http://localhost:8000/serverlogs/](http://localhost:8000/serverlogs/).
   - Select a PACS core, choose between Windows or Linux servers (as configured in the PACS core), and enter a predefined search or free text search.
   - Click the **Execute Search** button to initiate the search.

2. **View Results:**

   - The results of the executed search will display relevant log entries.
   - Results are sorted based on timestamps in descending order.

---

## Update Contact App

The `updatecontact` app manages and synchronizes professional contact details and facility assignments with an external EI (Enterprise Integration) system. It allows users to search for professionals by login name, retrieve and update professional details via an external API, refresh facility data, and manage facility groups.

---

### Models

#### Facility Model

- **Fields:**
  - **Name:** (CharField) The name of the facility.
  - **Facility ID:** (IntegerField) Unique identifier from the EI system.
  - **EI System:** (ForeignKey to `EISystem` from `timezone_updater`)

- **Methods:**
  - `__str__(self)`: Returns the facility name along with its ID.

#### FacilityGroup Model

- **Fields:**
  - **EI System:** (ForeignKey to `EISystem`)
  - **Name:** (CharField) The name of the facility group.
  - **Facilities:** (ManyToManyField to `Facility`)
  - **Last Modified:** (DateTimeField, auto-updated on modification)

- **Methods:**
  - `__str__(self)`: Returns the facility group name.

#### EIUser Model

- **Fields:**
  - **EI System:** (ForeignKey to `EISystem`)
  - **Login Name:** (CharField) The professional’s login name.
  - **Profession ID:** (IntegerField) Unique identifier for the professional.
  - **Last Updated:** (DateTimeField, auto-updated)
  - **Facility Groups:** (ManyToManyField to `FacilityGroup`, optional)

- **Methods:**
  - `__str__(self)`: Returns the login name and associated EI system.

- **Meta:**
  - Unique together on (`ei_system`, `login_name`, `profession_id`)

#### EIUserFacilityAssignment Model

- **Fields:**
  - **User:** (ForeignKey to `EIUser`)
  - **Facility:** (ForeignKey to `Facility`)
  - **Facility Group:** (ForeignKey to `FacilityGroup`, optional)
  - **Last Synced:** (DateTimeField, auto-updated)

- **Methods:**
  - `__str__(self)`: Returns a string combining the user’s login name and the facility name.

- **Meta:**
  - Unique together on (`user`, `facility`)

#### AppPermissions Model

- **Meta:**
  - Custom permission `use_updatecontact` is defined to control access to the update contact functionalities.

---

### Views (`updatecontact/views.py`)

The app includes several views that interact with the external EI system and manage local records.

#### `search_professional` View

- **Purpose:**  
  Searches for a professional by login name.
- **Key Functionality:**
  - Normalizes the login name and retrieves the selected EI system.
  - Obtains an authentication token for the EI system.
  - Calls the external API to retrieve professional details.
  - Processes facility assignments:
    - Extracts the current facilities assigned to the professional.
    - Retrieves available facilities and facility groups from the local database.
  - Creates or updates a local `EIUser` record.
  - Releases the token after processing.
  - Renders the `search_contact.html` template with the retrieved data.

#### `refresh_facilities` View

- **Purpose:**  
  Refreshes the list of facilities from the external EI system.
- **Key Functionality:**
  - Obtains an authentication token and calls the external API to retrieve facilities.
  - Filters and processes the facilities data.
  - Updates existing facility records or creates new ones in the local database.
  - Displays success or error messages.
  - Releases the token and redirects to the referring page.

#### `update_facilities` View

- **Purpose:**  
  Updates a professional's facility assignments.
- **Key Functionality:**
  - Acquires an authentication token and retrieves current professional details.
  - Updates the local `EIUser` record with facility group selections.
  - Constructs an updated list of facility assignments by merging current, available, and group-based facilities.
  - Pushes updates to the external EI system via an API call.
  - Updates the `last_updated` timestamp on the local record.
  - Releases the token and redirects to the search page with query parameters.

#### `manage_facility_groups` View

- **Purpose:**  
  Manages facility groups for an EI system.
- **Key Functionality:**
  - Displays facility groups for the selected EI system.
  - Allows users to update facility group memberships.
  - Provides an option to create a new facility group.
  - Uses concurrent processing to sync facility assignments for affected users.
  - Releases the token and shows success/error messages.

---

### Scripts (`updatecontact/scripts.py`)

This module provides helper functions to interact with the external EI system's API.

- **`get_token(ei_system)`**  
  Retrieves an authentication token from the EI system using provided credentials.
  
- **`get_professional_details(profession_id, ei_system, TOKEN)`**  
  Fetches detailed professional information from the EI system.
  
- **`update_professional_details(profession_id, ei_system, TOKEN, updated_details)`**  
  Updates professional details on the EI system with the provided data.
  
- **`release_token(ei_system, TOKEN)`**  
  Releases the authentication token after API operations.
  
- **`get_facilities_from_api(ei_system, TOKEN)`**  
  Retrieves a list of facilities from the EI system.
  
- **`sync_ei_user_facilities(user, ei_system, TOKEN)`**  
  Synchronizes an EI user's facility assignments with the EI system using concurrent processing.

---

### Admin Interface (`updatecontact/admin.py`)

- **FacilityAdmin:**
  - Displays facility name, facility ID, and associated EI system.
  - Provides filtering and searching capabilities.

- **FacilityGroupAdmin:**
  - Enables management of facility groups.
  - Uses a horizontal filter widget for facility selection.
  - Filters facilities based on the associated EI system when editing an existing group.

- **EIUserAdmin:**
  - Displays EI user details (login name, profession ID, EI system, last updated).
  - Supports filtering and searching, and includes a user-friendly interface for managing many-to-many relationships with facility groups.

---

### Templates

#### `search_contact.html`

- **Purpose:**  
  Provides a user interface for searching professionals by login name and selecting an EI system.
- **Key Elements:**
  - A dropdown to select an EI system.
  - A form field for entering the professional’s login name.
  - A link to manage facility groups.
  - Displays professional details, current facilities, available facilities, and facility groups if the professional is found.
  - Contains checkboxes for updating facility assignments.

#### `manage_groups.html`

- **Purpose:**  
  Allows users to manage facility groups.
- **Key Elements:**
  - Dropdowns for selecting an EI system and an existing facility group.
  - A form for refreshing available facilities from the EI system.
  - A section for creating a new facility group if one isn’t selected.
  - Checkboxes to display current and available facilities for the selected group.
  - JavaScript for dynamic UI interactions:
    - Synchronizing facility checkboxes when a facility group checkbox is toggled.
    - Displaying loading alerts during long-running operations.
    - Automatically removing alerts after a set period.

---

### How to Use

1. **Search for a Professional:**
   - Navigate to the search page (e.g., [http://localhost:8000/updatecontact/](http://localhost:8000/updatecontact/)).
   - Select an EI system and enter the professional’s login name.
   - Click **Search** to retrieve the professional’s details and facility assignments.

2. **Refresh Facilities:**
   - Use the refresh button to update the list of available facilities from the EI system.

3. **Update Facilities:**
   - Modify facility assignments and group selections for the professional.
   - Click **Update Facilities** to push the changes to the EI system.

4. **Manage Facility Groups:**
   - Navigate to the facility groups management page.
   - Select an EI system, update an existing group, or create a new group.
   - Adjust facility memberships and sync the changes with the EI system.

---

## Move Workstation App

The Move Workstation App is designed to facilitate the management of workstation assignments within an external EI system. It allows users to search for workstations, update their workstation groups, and register new workstations if they are not already present in the system.

---

### Models

#### WorkstationGroup Model

- **Fields:**
  - **wsg_id:** (IntegerField) Stores the workstation group ID from Oracle.
  - **Name:** (CharField) A friendly name for the workstation group.

- **Methods:**
  - `__str__(self)`: Returns the friendly name of the workstation group.

#### AppPermissions Model

- **Meta:**
  - Defines a custom permission `use_move_ei_workstations` to control access to this functionality.

---

### Views

The app provides two main views:

#### `move_workstation` View

- **Access:**  
  Requires the `use_move_ei_workstations` permission.
  
- **Functionality:**
  - Accepts both GET and POST requests.
  - On a **GET** request, it displays a form (via the `WorkstationForm`) to search for a workstation.
  - On a **POST** request:
    - Validates the form and retrieves the selected database alias, workstation name, and new group.
    - Executes an Oracle query (using a specified database connection) to search for a workstation.
    - If found:
      - Renders the workstation details and allows the user to update its workstation group.
      - If a new group is specified, the workstation group is updated in the database.
    - If not found:
      - Displays an option to create a new workstation.
  - Uses Django messages for success or error feedback.

#### `create_workstation` View

- **Access:**  
  CSRF-exempt and requires the `use_move_ei_workstations` permission.
  
- **Functionality:**
  - Accepts JSON POST data containing the workstation name and the EI system (database alias).
  - Validates the input and retrieves the corresponding EI system configuration.
  - Calls a helper function (`register_workstation`) to register the new workstation via an external EI API.
  - Returns a JSON response indicating success or error.

---

### Scripts (`MoveEIWorkstation/scripts.py`)

- **`register_workstation(ei_system, workstation_name)`**  
  - Retrieves an authentication token using helper functions from the update contact app.
  - Constructs and sends a POST request to the external EI API endpoint to register the workstation.
  - Releases the token after the operation.
  - Returns a JSON result with the status and message regarding the registration outcome.

---

### Forms

#### WorkstationForm

- **Fields:**
  - **db_alias:** (ChoiceField)  
    Populated from the `FriendlyDBName` model (from the Oracle query app) to select the database/EI system.
  - **workstation_name:** (CharField)  
    The name of the workstation (case sensitive).
  - **new_group:** (ModelChoiceField)  
    Optional field to select a new workstation group from the available `WorkstationGroup` records.

---

### Admin Interface

- The admin registers the `WorkstationGroup` model, allowing administrators to manage and configure workstation groups via Django’s admin interface.

---

### Templates

#### `move_workstation.html`

- **Purpose:**
  - Provides a user-friendly interface to search for a workstation, view its details, update its workstation group, and create a new workstation if needed.
  
- **Key Features:**
  - Displays the search form and workstation details.
  - If a workstation is found, shows current workstation information such as name, description, IP address, and current group.
  - Offers a form to update the workstation group.
  - If the workstation is not found, presents an option (via an AJAX button) to create a new workstation.
  - Implements JavaScript to handle AJAX requests, display processing status (with a timer), and provide immediate feedback to the user.

---

### How to Use

1. **Search for a Workstation:**
   - Navigate to the Move Workstation page (e.g., [http://localhost:8000/move_ei_workstations/](http://localhost:8000/move_ei_workstations/)).
   - Enter the workstation name and select the appropriate database/EI system from the dropdown.
   - Click **Search** to look up the workstation.

2. **Update Workstation Group:**
   - If the workstation is found, its current details are displayed.
   - Select a new workstation group from the provided options and submit the form.
   - The system updates the workstation’s group in the database and provides confirmation.

3. **Create a New Workstation:**
   - If the workstation is not found, an option to create a new workstation is presented.
   - Click the **Create Workstation** button to trigger an AJAX request that registers the workstation through the external EI API.
   - On success, the page refreshes to show the newly registered workstation details.

---

## Sites App

The `sites` app in this Django project manages a collection of site URLs and provides a simple interface to view them. Below is an outline of the components and functionalities within this app:

### Models

#### `SiteURL` Model

- **Fields:**
  - URL (URLField)
  - Description (TextField)

- **Methods:**
  - `__str__(self)`: Returns the description of the site URL.

### Admin Interface

- `SiteURL` model is registered in the admin interface.
- Provides an organized view for efficient management of site URLs.

### Permissions

- Custom permission `use_sites` is defined to control access to site URLs.

### URL Configuration (`sites/urls.py`)

- One URL pattern is defined:
  - `''` (Empty): Maps to the `index` view, displaying the list of site URLs.

### Views (`sites/views.py`)

#### `index` View

- Requires `use_sites` permission.
- Fetches all site URLs and renders the `sites.html` template with the list.

### How to Use

1. **View Sites:**

    - Navigate to the Sites app by visiting [http://localhost:8000/sites/](http://localhost:8000/sites/).
    - Access a list of site URLs with their descriptions.

## TimeZone Updater App

The `timezone_updater` app in this Django project facilitates the updating of time zones for external systems through API calls. Below is an outline of the components and functionalities within this app:

### Models

#### `EISystem` Model

- **Fields:**
  - Name (CharField)
  - EI FQDN (CharField)
  - EI User (CharField)
  - EI Password (CharField)

- **Methods:**
  - `__str__(self)`: Returns the name of the EI System.

### Admin Interface

- `EISystem` model is registered in the admin interface.
- Provides an organized view for efficient management of EI Systems.

### Permissions

- Custom permission `use_timezone_updater` is defined to control access to the TimeZone Updater.

### Scripts (`timezone_updater/scripts.py`)

- Contains functions to interact with external systems using API calls.
- Includes functions to get the API auth token, search for an external system, update its timezone, and release the token.

### URL Configuration (`timezone_updater/urls.py`)

- Two URL patterns are defined:
  - `''`: Maps to the `timezone_update` view, displaying the timezone update interface.
  - `timezone_update/`: Maps to the `timezone_update` view, handling the timezone update process.

### Views (`timezone_updater/views.py`)

#### `timezone_update` View

- Requires `use_timezone_updater` permission.
- Displays an interface to look up and update time zones for external systems.
- Implements functionality to:
  - Look up the current timezone based on the external system code.
  - Update the timezone for an external system.

### How to Use

1. **TimeZone Update:**

   - Navigate to the TimeZone Updater app by visiting [http://localhost:8000/timezone_updater/](http://localhost:8000/timezone_updater/).
   - Select an EI System and enter the external system code to look up or update time zones.


---

## EI Cluster Node Status App

The EI Cluster Node Status App monitors the health of cluster nodes in an external EI system. It retrieves a list of available node IP addresses from the EI system via an API, checks each node’s health status through HTTPS requests, and displays the results in a user-friendly table.

---

### Models

#### AppPermissions Model

- **Purpose:**  
  Defines custom permissions for the app.
  
- **Details:**  
  - Custom permission `use_ei_status` controls access to the EI Cluster Node Status functionality.

---

### Views

#### `index` View

- **Access:**  
  Requires the `use_ei_status` permission.

- **Functionality:**  
  - Displays a form (`EISystemForm`) that lets users select an EI System.
  - On POST, retrieves the selected EI System and calls the external EI API to get a list of available cluster nodes.
  - Uses helper functions to:
    - Obtain an authentication token.
    - Call the cluster API to get node data.
    - Check the health of each node (including hostname lookup and retry logic).
  - Renders the `status_page.html` template with the following:
    - Node statuses (IP address, hostname, health status, and number of retries).
    - Selected EI System details and the current time.
  - Disables caching to ensure up-to-date status information.

---

### Helper Functions / Scripts

- **`get_token(ei_system)`**  
  Obtains an authentication token from the EI system’s authentication endpoint using the system's credentials.

- **`release_token(ei_system)`**  
  Releases the authentication token by calling the EI system’s logout endpoint.

- **`call_cluster_api(ei_system)`**  
  Uses the authentication token to call the EI system’s API endpoint (`/ris/web/v2/queues/availableNodes`) and retrieve a list of available cluster nodes.

- **`check_cluster_node_health(ip_address, max_retries=2)`**  
  Checks a node’s health by making an HTTPS GET request to its `/status` endpoint. Retries the request if necessary, and returns both the health status and the number of retries performed.

- **`check_single_node(ip_address)`**  
  Retrieves the hostname associated with an IP address and checks its health status using `check_cluster_node_health`.

- **`check_cluster_nodes(cluster_nodes)`**  
  Extracts IP addresses from the raw cluster node data and concurrently checks each node's health using a thread pool.

---

### Forms

#### `EISystemForm`

- **Purpose:**  
  Provides a dropdown for users to select an EI System.
  
- **Details:**  
  - Populated from the `EISystem` model.

---

### Templates

#### `index.html`

- **Purpose:**  
  Displays a form for selecting an EI System.
  
- **Key Elements:**  
  - A dropdown list of available EI Systems.
  - A submit button to initiate the status check.

#### `status_page.html`

- **Purpose:**  
  Displays the health status of the cluster nodes.
  
- **Key Elements:**  
  - The name of the selected EI System and the timestamp of the check.
  - A section showing the raw cluster node response.
  - A table listing each node with:
    - IP address
    - Hostname
    - Health status (including error details if applicable)
    - Number of retries performed
  - A link to return to the EI System selection page.

---

### How to Use

1. **Select an EI System:**
   - Navigate to the EI Cluster Node Status page (e.g., [http://localhost:8000/ei_status/](http://localhost:8000/ei_status/)).
   - Choose an EI System from the dropdown and submit the form.

2. **View Cluster Node Status:**
   - The app retrieves the list of available cluster nodes from the selected EI System.
   - It concurrently checks each node’s health and displays the results in a table on the status page.

3. **Refresh Status:**
   - Click the "Back" link to return to the selection page and re-run the status check as needed.

---

    
## Web Server Maintenance App

The `webservermaintenance` app in this Django project provides functionality for executing remote commands on web servers, maintaining logs of executed commands. Below is an outline of the components and functionalities within this app:

### Models

#### `CommandLog` Model

- **Fields:**
  - User (ForeignKey to `User` model)
  - Timestamp (DateTimeField, auto_now_add=True)
  - Command (CharField, max_length=200)
  - Result (TextField)

- **Methods:**
  - `__str__(self)`: Returns a string representation of the command log.

#### `RemoteServer` Model

- **Fields:**
  - Name (CharField, max_length=255, unique=True)
  - Friendly Name (CharField, max_length=255)
  - Hostname (CharField, max_length=255)
  - Username (CharField, max_length=255)
  - Private Key Path (CharField, max_length=512)

- **Methods:**
  - `__str__(self)`: Returns the name of the remote server.

#### `RemoteCommand` Model

- **Fields:**
  - Name (CharField, max_length=255, unique=True)
  - Command (TextField)

- **Methods:**
  - `__str__(self)`: Returns the name of the remote command.

### Admin Interface

- `CommandLog`, `RemoteServer`, and `RemoteCommand` models are registered in the admin interface.
- Provides an organized view for efficient management of command logs, remote servers, and remote commands.

### Permissions

- Custom permission `use_webserverMaintenance` is defined to control access to the Web Server Maintenance functionality.

### Scripts (`webservermaintenance/urls.py`)

- Defines URL patterns for the Web Server Maintenance app, including paths for the main page, executing remote commands, and other paths for additional functionalities.

### Utility Functions (`webservermaintenance/utils.py`)

- Includes the `execute_remote_command` function using `paramiko` to execute remote commands on web servers and log the results.

### Views (`webservermaintenance/views.py`)

#### `index` View

- Requires `use_webserverMaintenance` permission.
- Renders the main page for the Web Server Maintenance app.

#### `execute_remote_command_by_server_and_command_name` View

- Requires `use_webserverMaintenance` permission.
- Handles the execution of remote commands based on the specified server and command name.
- Logs the command execution details.

#### `main_page` View

- Requires `use_webserverMaintenance` permission.
- Renders the main page for the Web Server Maintenance app, listing available remote servers.

### How to Use

1. **Web Server Maintenance:**

   - Navigate to the Web Server Maintenance app by visiting [http://localhost:8000/webservermaintenance/](http://localhost:8000/webservermaintenance/).
   - Explore functionalities for executing remote commands on web servers, viewing logs, and managing remote servers and commands.

# Project Settings - Settings.py

This file (`JSF/Settings.py`) contains configuration settings for your Django project. Here's an overview of key sections and considerations:

## Logging Configuration

The `LOGGING` section configures logging settings, including log file paths and loggers for `django_auth_ldap` and `audit_queries`.

## Fernet Encryption Keys

`FERNET_KEYS` should contain a list of Fernet encryption keys used for sensitive data encryption in your project.

## Allowed Hosts and Reverse Proxy Settings

`ALLOWED_HOSTS` specifies valid hostnames for your application. Reverse proxy settings (`SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`, `USE_X_FORWARDED_HOST`) are configured for proxy environments.

## Installed Apps

The `INSTALLED_APPS` list includes all Django apps used in the project, including custom ones like `webserverMaintenance`, `sites`, etc.

## Middleware

`MIDDLEWARE` defines the middleware stack, including security and custom middleware (`custom_modules.middleware.CustomPermissionMiddleware`).

## Template Configuration

`TEMPLATES` configures template settings, including the location of shared templates.

## Database Configuration

The `DATABASES` section configures the default SQLite database and additional Oracle databases (`impax_db_example`, `ei_db_example`).

## Password Validation

`AUTH_PASSWORD_VALIDATORS` specifies password validation requirements.

## LDAP Authentication

`AUTHENTICATION_BACKENDS` includes LDAP authentication using `django_auth_ldap`. Adjust LDAP server details (`AUTH_LDAP_SERVER_URI`, `AUTH_LDAP_BIND_DN`, etc.) as per your LDAP setup.

## LDAP User and Group Mapping

`AUTH_LDAP_USER_ATTR_MAP` maps LDAP attributes to Django user fields. Group mapping is configured in `AUTH_LDAP_GROUP_SEARCH` and related settings.

## Caching

`CACHES` defines caching settings, using the default LocMemCache for simplicity. Adjust for production environments.

## Static Files

`STATIC_URL` and `STATICFILES_DIRS` specify the URL and directories for serving static files.

## Miscellaneous

Other settings include `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `SESSION_COOKIE_AGE`.

Remember to replace placeholder values with your actual configurations.


## How to Set Up the Django Project

Follow these steps to set up and run the Django project:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/mrjmc99/JSF.git
    cd JSF
    ```

2. **Create Virtual Environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate Virtual Environment:**

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source venv/bin/activate
        ```

4. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Apply Database Migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Create Superuser (Optional):**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the Development Server:**

    ```bash
    python manage.py runserver
    ```

8. **Access the Admin Interface:**

    Open your browser and go to [http://localhost:8000/admin/](http://localhost:8000/admin/). Log in using the superuser credentials created in step 6.

## Reverse Proxy Configuration (IIS)

## IIS Reverse Proxy Configuration

If you plan to use Internet Information Services (IIS) as a reverse proxy for your Django application, you can use the following sample `web.config` file as a starting point:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <!-- Rule for static files -->
                <rule name="Static Files" enabled="true" stopProcessing="true">
                    <match url="static/.*" />
                    <action type="Rewrite" url="{R:0}" />
                    <conditions>
                        <add input="{REQUEST_URI}" pattern="^/admin/.*" negate="true" />
                    </conditions>
                </rule>

                <!-- Rule for reverse proxy -->
                <rule name="ReverseProxyInboundRule1" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:8000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
        <staticContent>
            <mimeMap fileExtension=".webp" mimeType="image/webp" />
        </staticContent>
    </system.webServer>
</configuration>
```


## Additional Notes

- These Apps have been tested with Agfa Enterprise Imaging 8.2.0 and might require adjustments to support newer versions.

## Issues and Support

If you encounter any issues or have questions, please create an issue in the [GitHub repository](https://github.com/mrjmc99/JSF).


## Todo
- Move away from IIS for reverse proxy