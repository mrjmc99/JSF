# webservermaintenance/urls.py
import paramiko
from webserverMaintenance.models import CommandLog

def execute_remote_command(hostname, username, private_key_path, command, user):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, key_filename=private_key_path)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Log the command execution details
        CommandLog.objects.create(
            user=user,
            command=command,
            result=f"Output: {output} Error: {error}"
        )

        result = {'output': output, 'error': error}
        ssh.close()
        return result
    except Exception as e:
        print(f"Error executing remote command: {e}")
        return None
