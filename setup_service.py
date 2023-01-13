import os

script_path = os.path.join(os.path.dirname(__file__), "src/main.py")

with open("apriltag_detector.service") as source:
    source_content = map(lambda x: x.replace("%s", script_path), source.readlines())

    with open("/etc/systemd/system/apriltag_detector.service") as destination:
        destination.writelines(source_content)