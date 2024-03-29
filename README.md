# JSF

## Introduction

This Django project is designed for [provide a brief description of the project]. It consists of several Django apps, each serving a specific purpose. Below are the apps along with their functionalities.

## Project Structure

## Audit Queries App

The `audit_queries` app in this Django project is designed to manage audit queries and execute them to retrieve relevant data from specified databases. Here's an overview of the components and functionalities within this app:

### Models

#### `AuditQuery` Model

- **Fields:**
  - Name (CharField, unique)
  - Description (TextField, optional)
  - Query (TextField)
  - Variables (JSONField, optional)
  - Created At (DateTimeField, auto-generated)
  - Updated At (DateTimeField, auto-updated)
  - Database (ForeignKey to `FriendlyDBName`)
  - Multiple Queries (BooleanField, default: False)
  - Requires Preliminary (BooleanField, default: False)
  - Preliminary Query (TextField, optional, help_text: "SQL query to fetch extra data needed for the main query")
  - Preliminary DB (ForeignKey to `FriendlyDBName`, optional, related_name: "preliminary_queries", help_text: "Database to run the preliminary query against")

- **Methods:**
  - `__str__(self)`: Returns the name of the audit query.

#### `SubQuery` Model

- **Fields:**
  - Parent Query (ForeignKey to `AuditQuery`)
  - Query (TextField)
  - Order (PositiveIntegerField)
  - Database (ForeignKey to `FriendlyDBName`)

### Admin Interface

- Customized admin interface is provided for efficient management.
- `AuditQueryAdmin` and `SubQueryAdmin` classes are registered to facilitate admin operations.
- Various fields are displayed, and search and filtering options are available.

### Permissions

- A custom permission `use_audit_queries` is defined, allowing users to utilize audit queries.

### URL Configuration (`audit_queries/urls.py`)

- Two URL patterns are defined:
  1. `''` (Empty): Points to the `audit_query_list` view.
  2. `'execute/<int:query_id>/'`: Maps to the `execute_audit_query` view, allowing the execution of a specific audit query.

### Views (`audit_queries/views.py`)

#### `audit_query_list` View

- Displays a list of available audit queries.
- Utilizes the `list.html` template to render the queries.

#### `execute_audit_query` View

- Executes a specific audit query and displays its results.
- Retrieves query parameters from the user input.
- Handles preliminary queries if required.
- Executes main and subqueries.
- Renders the `conversion_results.html` template with query results.

#### `fetch_audit_data` Function

- A utility function to fetch data for an audit query from a specified server.

### How to Use

1. **List Available Audit Queries:**

    - Access the URL [http://localhost:8000/audit_queries/](http://localhost:8000/audit_queries/) after running the development server.

2. **Execute Specific Audit Query:**

    - Access the URL [http://localhost:8000/audit_queries/execute/{query_id}/](http://localhost:8000/audit_queries/execute/{query_id}/) to execute a specific audit query.

### Permissions

- To use audit queries, users need the `use_audit_queries` permission.


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

The `serverlogs` app in this Django project manages and searches through server logs stored on remote Windows servers. It provides functionality to connect to these servers, retrieve logs, and perform searches. Below is an outline of the components and functionalities within this app:

### Models

#### `PACSCore` Model

- **Fields:**
  - Name (CharField, unique)
  - Description (TextField)

- **Methods:**
  - `__str__(self)`: Returns the name of the PACS core.

#### `RemoteWindowsServer` Model

- **Fields:**
  - Core (ForeignKey to `PACSCore`)
  - Name (CharField)
  - IP Address (GenericIPAddressField)
  - Credentials (EncryptedCharField)
  - Logs Folder (CharField)

- **Methods:**
  - `__str__(self)`: Returns a formatted string with the server name and associated PACS core.

#### `PredefinedSearch` Model

- **Fields:**
  - Name (CharField)
  - Search Query (TextField)

- **Methods:**
  - `__str__(self)`: Returns the name of the predefined search.

### Admin Interface

- `PACSCore`, `RemoteWindowsServer`, and `PredefinedSearch` models are registered in the admin interface.
- Provides an organized view for efficient management of PACS cores, remote servers, and predefined searches.

### Permissions

- Custom permission `use_serverLogs` is defined to control access to server logs.

### URL Configuration (`serverlogs/urls.py`)

- Two URL patterns are defined:
  - `''` (Empty): Maps to the `search_logs` view, displaying the search page.
  - `'execute/'`: Maps to the `execute_search` view, allowing the execution of a search.

### Views (`serverlogs/views.py`)

#### `search_logs` View

- Requires `use_serverLogs` permission.
- Fetches all PACS cores and predefined searches.
- Renders the `search_logs.html` template with available options.

#### `execute_search` View

- Requires `use_serverLogs` permission.
- Executes a search on the selected PACS core and predefined search or free text.
- Processes server logs in parallel and retrieves search results.

### Log Processing Functions

- `extract_log_details(log_message)`: Extracts details like reason, calling AE, and called AE from a log message.
- `extract_and_convert_timestamp(timestamp_line)`: Extracts and converts a timestamp from a log file line.
- `process_log_file(log_file_path, search_text, results_list)`: Processes a log file for a specific search text.
- `process_server(server, search_text, results_list)`: Processes logs for a specific server in parallel.

### How to Use

1. **Search Logs:**

    - Navigate to the Server Logs app by visiting [http://localhost:8000/serverlogs/](http://localhost:8000/serverlogs/).
    - Select a PACS core and enter a predefined search, or perform a free text search.
    - Click on the 'Execute Search' button to initiate the search.

2. **View Results:**

    - View the results of the executed search, displaying relevant log entries.
    - Results are sorted based on timestamps in descending order.

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