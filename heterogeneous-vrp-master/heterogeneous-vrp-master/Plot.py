# requires matplotlib package (https://matplotlib.org)
import matplotlib.pyplot as plt
# draw nodes and routes
# requires list of routes R = [[0,..,0],..], i.e., list of list of visits
def draw_routes(R, nodes):
    # set color scheme
    # https://matplotlib.org/3.2.1/gallery/color/colormap_reference.html

    colors = plt.cm.get_cmap('tab10', len(R))

    fig, ax = plt.subplots()

    for r_idx, r in enumerate(R):
        path = list()
        for i in range(len(r)):
            path.append((nodes[r[i]]['lon'], nodes[r[i]]['lat']))

        # plot control points and connecting lines
        x, y = zip(*path)
        line, = ax.plot(x, y, 'o-', color=colors(r_idx))

    ax.plot(nodes[0]['lon'], nodes[0]['lat'], 'ks')

    # ax.grid()
    ax.axis('equal')

    # hide axis labels
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)

    # hide bounding box
    # for pos in ['right', 'top', 'bottom', 'left']:
    #     plt.gca().spines[pos].set_visible(False)

    plt.show()
