from flask import Flask, Response
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def index():
    # Create a figure and axis with equal aspect ratio
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')

    # Draw a dashed circle for reference
    circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
    ax.add_artist(circle)

    # Define the arrows' angles (in degrees) and corresponding labels
    angles_deg = [315, 45, 135, 225]
    labels = ["Big L", "small-c", "Big C", "small-l"]

    # Draw each arrow starting at the origin and annotate with its label
    for angle, label in zip(angles_deg, labels):
        rad = np.deg2rad(angle)
        dx, dy = np.cos(rad), np.sin(rad)
        ax.arrow(0, 0, dx, dy, head_width=0.05, head_length=0.1, fc='k', ec='k')
        ax.text(1.15 * dx, 1.15 * dy, label, ha='center', va='center', fontsize=12)

    # Remove axis ticks and add a title for clarity
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Campus Political Compass: Four Factions")

    # Save the plot to a BytesIO buffer and return as a PNG image
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return Response(buf.getvalue(), mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)