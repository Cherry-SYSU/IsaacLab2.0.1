# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
This script demonstrates how to simulate bipedal robots.

.. code-block:: bash

    # Usage
    ./isaaclab.sh -p source/standalone/demos/bipeds.py

"""

"""Launch Isaac Sim Simulator first."""

import argparse
import torch

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="This script demonstrates how to simulate bipedal robots.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.sim import SimulationContext

##
# Pre-defined configs
# ##
# from isaaclab.assets.cassie import CASSIE_CFG  # isort:skip
# from isaaclab.assets import H1_CFG  # isort:skip
# from isaaclab.assets import G1_CFG  # isort:skip
from isaaclab_assets import G1_MINIMAL_CFG, BRUCE_CFG  

def main():
    """Main function."""
    # Load kit helper
    sim_cfg = sim_utils.SimulationCfg(dt=0.005, device=args_cli.device)
    sim = SimulationContext(sim_cfg)
    # Set main camera
    sim.set_camera_view(eye=[3.0, 0.0, 2.25], target=[0.0, 0.0, 1.0])

    # Spawn things into stage
    # Ground-plane
    cfg = sim_utils.GroundPlaneCfg()
    cfg.func("/World/defaultGroundPlane", cfg)
    # Lights
    cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
    cfg.func("/World/Light", cfg)

    # Define origins
    origins = torch.tensor([
        [0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 2.0, .0],
    ]).to(device=sim.device)

    # Robots
    # cassie = Articulation(CASSIE_CFG.replace(prim_path="/World/Cassie"))
    # h1 = Articulation(H1_CFG.replace(prim_path="/World/H1"))
    # g1 = Articulation(G1_CFG.replace(prim_path="/World/G1"))
    bruce =  Articulation(BRUCE_CFG.replace(prim_path="/World/BRUCE"))
    robots = [bruce ]

    # Play the simulator
    sim.reset()

    # Now we are ready!
    print("[INFO]: Setup complete...")

    # Define simulation stepping
    sim_dt = sim.get_physics_dt()
    sim_time = 0.0
    count = 0
    # Simulate physics
    while simulation_app.is_running():
        # reset
        if count % 1700 == 0:
            # reset counters
            sim_time = 0.0
            count = 0
            for index, robot in enumerate(robots):
                # reset dof state
                joint_pos, joint_vel = robot.data.default_joint_pos, robot.data.default_joint_vel
                robot.write_joint_state_to_sim(joint_pos, joint_vel)
                print(joint_pos)
                pos = robots[0].data.joint_pos
                print("8"*10)
                print(pos)
                root_state = robot.data.default_root_state.clone()
                root_state[:, :3] += origins[index]
                robot.write_root_state_to_sim(root_state)
                robot.reset()
            # reset command
            # print(">>>>>>>> Reset!")
            # apply action to the robot
        #归零
        # if count % 100 == 0:
        #     for robot in robots:
        #         pos = torch.zeros_like(robot.data.default_joint_pos.clone())
        #         id  = int(count/100 %16)
        #         pos[0, id]=0.0001
        #         print(id)
        #         robot.set_joint_position_target(pos)
        #         robot.write_data_to_sim()
            # perform step
        
        # apply actins
        # # generate random joint positions
        joint_pos_target = robot.data.default_joint_pos
        print(robot.data.root_pos_w[:,2],"height")
        # # apply action to the robot
        robot.set_joint_position_target(joint_pos_target)
        # # write data to sim
        robot.write_data_to_sim()
        # pos = robots[0].data.joint_pos
                #----------------
        # print(pos)
        sim.step()
        # update sim-time
        sim_time += sim_dt
        count += 1
        # update buffers
        for robot in robots:
            robot.update(sim_dt)


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
