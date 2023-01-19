import os

base_path = os.path.dirname(__file__)
script_path = "src/main.py"

with open("apriltag_detector.service", "r") as source:
    source_content = map(lambda x: x.replace("%s", script_path).replace("%p", base_path), source.readlines())

    with open("/etc/systemd/system/apriltag_detector.service", "w") as destination:
        destination.writelines(source_content)