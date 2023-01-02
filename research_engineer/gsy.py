### SIMULATION

import pandapower as pp

#create empty net
net = pp.create_empty_network() 

#create buses
b1 = pp.create_bus(net, vn_kv=20., name="Bus 1")
b2 = pp.create_bus(net, vn_kv=0.4, name="Bus 2")
b3 = pp.create_bus(net, vn_kv=0.4, name="Bus 3")

#create bus elements
pp.create_ext_grid(net, bus=b1, vm_pu=1.02, name="Grid Connection")
pp.create_load(net, bus=b3, p_mw=0.1, q_mvar=0.05, name="Load")

#create branch elements
tid = pp.create_transformer(net, hv_bus=b1, lv_bus=b2, std_type="0.4 MVA 20/0.4 kV", name="Trafo")
pp.create_line(net, from_bus=b2, to_bus=b3, length_km=0.1, name="Line",std_type="NAYY 4x50 SE")   


def run_simulation():
    pp.runpp(net)
    return net

# REST API

from flask import Flask, request, jsonify
import os

# Create a Flask app
app = Flask(__name__)

# Define an endpoint for running the power flow simulation and returning the results
@app.route("/grid-power-analysis/", methods=["GET"])
def get_results():
    # Load the pandapower network from the input data
    net = pp.from_json(request.args.get("network"))

    # Run the power flow simulation
    net = run_simulation(net)
    
    # Extract the active and reactive power for each node in the grid
    results = {
        "loads": {
            load.name: (load.p_mw, load.q_mvar)
            for _, load in net.load.iterrows()
        },
        "generators": {
            gen.name: (gen.p_mw, gen.q_mvar)
            for _, gen in net.gen.iterrows()
        },
        "external_grid": {
            ext_grid.name: (ext_grid.p_mw, ext_grid.q_mvar)
            for _, ext_grid in net.ext_grid.iterrows()
        }
    }

    # Return the results as a JSON response
    return jsonify(results)

app.run()
