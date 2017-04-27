import gmaps
import gmaps.datasets
gmaps.configure(api_key="AIzaSyCUKCF4ZffOzQc4L2fVeJDPZ-kFLYsw3RI") # Your Google API key

# load a Numpy array of (latitude, longitude) pairs
def plot(locations):
    m = gmaps.Map()
    pts_layer = gmaps.symbol_layer(
        locations, fill_color="red", stroke_color="red", scale=1
    )
    m = gmaps.Map()
    m.add_layer(pts_layer)
    return m