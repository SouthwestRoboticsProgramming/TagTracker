import cv2
from argparse import ArgumentParser

def main():
    # Create a parser for optional parameters
    parser = ArgumentParser(prog='Camera Port Scanner',
                            description='Camera Port Scannera')
    parser.add_argument('--min', type=int, default=-10, metavar='', help='Min port to scan')
    parser.add_argument('--max', type=int, default=10, metavar='', help='Max port to scan')

    args = parser.parse_args()
    min_port = args.min
    max_port = args.max

    if (min_port >= max_port):
        raise ValueError('Make sure the minimum port is less than the maximum!')

    working_ids = []
    for i in range(min_port, max_port):
        cap = cv2.VideoCapture(i)

        if cap.isOpened():
            working_ids.append(i)

        cap.release()

    print('Working Camera Ports: \n \
    {}'.format(working_ids))

if __name__ == '__main__':
    main()