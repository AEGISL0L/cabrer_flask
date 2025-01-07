import subprocess
import re

# Absolute path to requirements.txt
req_file = '/srv/www/farmacabrer.com/public_html/requirements.txt'
# Log file to record installation errors
log_file = '/srv/www/farmacabrer.com/public_html/install_errors.log'

# Clear the log file
with open(log_file, 'w') as f:
    pass

with open(req_file, 'r') as f:
    for line in f:
        package = line.strip()
        if package and not package.startswith('#'):
            print(f"Installing {package}")
            try:
                # Attempt to install the package
                subprocess.check_call(['pip', 'install', package])
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}")
                # Write the error to the log file
                with open(log_file, 'a') as log_f:
                    log_f.write(f"Failed to install {package}\n")
                    # Optionally, capture the error output
                    error_output = e.output if hasattr(e, 'output') else ''
                    log_f.write(f"Error: {error_output}\n")
                # Continue to the next package
