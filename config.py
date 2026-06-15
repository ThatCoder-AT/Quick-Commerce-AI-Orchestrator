import os

# Set this to the sandbox directory you created in the previous step.
# For Windows, use r"C:\qcomm_profile". 
# For Mac/Linux, use os.path.expanduser("~/qcomm_profile")
USER_DATA_DIR = r"C:\qcomm_profile" 

PROFILE_DIRECTORY = "Default"

# Framework Settings
TIMEOUT = 10 
HEADLESS = False # Keep False to effectively bypass anti-bot walls

# Supported Platforms
PLATFORMS = ["Blinkit", "Zepto", "Instamart", "JioMart", "BigBasket"]