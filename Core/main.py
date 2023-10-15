from node import Node


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--node_number", type=int, help="index of the in address-list-dictionary between 0 and 2 and also 3 is client"
        ,required=True
    )
    node = None
    args = parser.parse_args()
    if 0 <= args.node_number <=2:
        node = Node(args.node_number,NODES_DICTIONARY)
        node.start_node()
    elif args.node_number == 3:
        node = Client(NODES_DICTIONARY)
        node.start_node()



if __name__ == '__main__':
    main()