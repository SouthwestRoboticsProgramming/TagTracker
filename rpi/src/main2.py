import json
import sys

from networktables import NetworkTablesInstance

DEFAULT_CONFIG_PATH = '/boot/frc.json'
# DEFAULT_CONFIG_PATH = 'frc.json'


def extract_config(path):
    team = 0
    is_server = False
    camera_configs = []
    switched_configs = []

    # Extract into json
    try:
        with open(path, 'rt', encoding='utf-8') as file:
            config = json.load(file)
    except OSError as e:
        raise FileNotFoundError(f"Couldn't find {path}") from e

    # Check that the json is formatted correctly
    if not isinstance(config, dict):
        raise TypeError("json not formatted correctly")

    # Extract team number
    team = config['team']
    if team is None:
        raise KeyError('No team number defined')
    
    # Check if it should be client or server (optional config)
    if 'ntmode' in config:
        mode = config['ntmode'].lower()
        if mode == 'client':
            is_server = False
        elif mode == 'server':
            is_server = True
        else:
            raise NameError(f"Couldn't understand ntmode {mode} in config file")
    
    # Extract USB cameras
    camera_configs = config.get('cameras')
    if camera_configs is None:
        raise KeyError("No cameras defined!")

    # Extract switched cameras
    if 'switched cameras' in config:
        switched_configs = config['switched cameras']

    return team, is_server, camera_configs, switched_configs
    

def main():
    # Default config path is "/boot/frc.json" for WPILibPI
    configPath = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_CONFIG_PATH

    team, is_server, camera_configs, switched_configs = extract_config(configPath)

    # Start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if is_server:
        print("Starting NetworkTables server")
        ntinst.startServer()
    else:
        print(f"Connecting to NetworkTables for team {team}")
        print(type(team))
        ntinst.startClientTeam(team)
        ntinst.startDSClient()

    # Create a table to publish values to
    table = ntinst.getTable('tagtracker')

    # Configure cameras (TODO)

    # Loop until power is cut
    i = 0
    while True:
        table.putNumber("Test value", i)
        i+=1

if __name__ == '__main__':
    main()


    