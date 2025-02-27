import ezdxf
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

def load_dxf_profile(filename, resolution):
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    # msp = [entity for entity in msp if entity.dxftype() not in {"TEXT", "MTEXT"} and entity.]

    lines = []

    for entity in msp:
        print(entity.dxftype())


        # Extract points
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            num_points = int(np.linalg.norm(start-end)/resolution)+1
            points = np.round(np.linspace(start, end, num_points), 3)

            lines.append(points)

        elif entity.dxftype() == "ARC":
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = np.radians(entity.dxf.start_angle)
            end_angle = np.radians(entity.dxf.end_angle)
            if end_angle < start_angle:
                end_angle += 2 * np.pi  # Ensure proper ordering

            num_points = int((end_angle-start_angle) * radius/resolution) + 1

            angles = np.linspace(start_angle, end_angle, num_points)
            points = np.array([[float(round(center.x + radius * np.cos(a), 3)),
                                float(round(center.y + radius * np.sin(a), 3)), 0.0] for a in angles])

            lines.append(points)

        elif entity.dxftype() == "SPLINE":
            control_points = np.array(entity.control_points)

            length = sum([np.linalg.norm(control_points[i] - control_points[i+1]) for i in range(len(control_points)-1)])
            num_points = int(length/resolution)+1
            sampling_pts = np.linspace(0, 1, num_points)
            spline, u = splprep(control_points.T, s=0)
            x, y, z = np.round(np.array(splev(sampling_pts, spline)), 3)
            points = [[x[i], y[i], z[i]] for i in range(len(x))]
            lines.append(points)

    print(lines)
    for line in lines:
        print(type(line))


    merged = lines.pop(0).tolist()
    while lines:
        for i, line in enumerate(lines):
            if np.allclose(line[0], merged[-1]):  # Line starts where merged ends
                merged.extend(line[1:])  # Append without duplicating first point
                lines.pop(i)
                break
            elif np.allclose(line[-1], merged[0]):  # Line ends where merged starts
                merged = line[:-1].tolist() + merged  # Prepend without duplicating last point
                lines.pop(i)
                break
            elif np.allclose(line[-1], merged[-1]):  # Line reversed at end
                merged.extend(line[-2::-1])  # Reverse and append
                lines.pop(i)
                break
            elif np.allclose(line[0], merged[0]):  # Line reversed at start
                merged = line[1:][::-1].tolist() + merged  # Reverse and prepend
                lines.pop(i)
                break

    merged = np.array(merged)
    # plt.scatter(merged[:, 0], merged[:, 1])
    # plt.show()

    return merged




    # # Convert to NumPy array (assuming x-z plane, ignoring y)
    # points = np.array([(p[0], p[1]) for p in points])
    #
    # # Interpolate points
    # distances = np.cumsum(np.insert(np.linalg.norm(np.diff(points, axis=0), axis=1), 0, 0))
    # new_distances = np.linspace(0, distances[-1], num_points)
    # interp_points = np.column_stack([
    #     np.interp(new_distances, distances, points[:, 0]),
    #     np.interp(new_distances, distances, points[:, 1])
    # ])
    #
    # return interp_points


profile_points = load_dxf_profile("Test_dxf.DXF", 0.5)

print(profile_points)

plt.plot(profile_points[:, 0], profile_points[:, 1])
plt.show()
