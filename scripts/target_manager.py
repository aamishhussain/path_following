#!/usr/bin/env python

import rospy
import sys
import os
import math
import csv

from nav_msgs.msg import Odometry
from gazebo_msgs.msg import ModelStates 
from std_msgs.msg import Int64
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from std_msgs.msg import String

car_name        = str(sys.argv[1])
trajectory_name = str(sys.argv[2])
adaptive_lookahead  = str(sys.argv[3])
ang_lookahead_dist  = float(sys.argv[4])

plan = []

#index_pub = rospy.Publisher('/{}/purepursuit_control/index_nearest_point'.format(car_name), Int64, queue_size = 1)
#min_pose_pub  = rospy.Publisher('/{}/purepursuit_control/visualize_nearest_point'.format(car_name), PoseStamped, queue_size = 1)
#index_change_pub = rospy.Publisher('/{}/purepursuit_control/change_the_index'.format(car_name), Bool, queue_size = 1)


global plan_size
global seq

plan         = []
frame_id     = 'map'
seq          = 0
ang_goal_pub = rospy.Publisher('/{}/purepursuit_control/ang_goal'.format(car_name), PoseStamped, queue_size = 1)
vel_goal_pub = rospy.Publisher('/{}/purepursuit_control/vel_goal'.format(car_name), PoseStamped, queue_size = 1)
plan_size    = 0

global current_index

current_index = 0
global threshold 

threshold = 0.2


brake_lookahead        = 2.00
caution_lookahead      = 2.50
unrestricted_lookahead = 3.00

global ang_lookahead_dist
global vel_lookahead_dist


def construct_path():
    global plan_size
    file_path = os.path.expanduser('/home/sim/f1-10-simulator/catkin_ws/src/path_following/path/{}.csv'.format(trajectory_name))

    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ';')
        for waypoint in csv_reader:
            plan.append(waypoint)

    for index in range(0, len(plan)):
        for point in range(0, len(plan[index])):
            plan[index][point] = float(plan[index][point])

    plan_size = len(plan)        


def check_threshold(curr_x, curr_y):
    global current_index
    global threshold 
    change_index=0
    
    eucl_x = math.pow(curr_x - plan[current_index][1], 2)
    eucl_y = math.pow(curr_y - plan[current_index][2], 2)
    eucl_d = math.sqrt(eucl_x + eucl_y)
    if  current_index == (len(plan)-1) and threshold >= eucl_d:
        current_index =0
    elif current_index != (len(plan)-1) and threshold >= eucl_d: 
        current_index +=1  


    return            

def odom_callback(data):

    global seq
    global plan_size
    global ang_lookahead_dist
    global vel_lookahead_dist
    global current_index

    curr_x         = data.pose[1].position.x
    curr_y         = data.pose[1].position.y
    check_threshold(curr_x, curr_y)

    pose_index = (current_index + ang_lookahead_dist) % plan_size
    
    print (pose_index)
    print "is the index"
    goal                    = PoseStamped()
    goal.header.seq         = seq
    goal.header.stamp       = rospy.Time.now()
    goal.header.frame_id    = frame_id
    goal.pose.position.x    = plan[pose_index][1]
    goal.pose.position.y    = plan[pose_index][2]
    goal.pose.orientation.z = 0
    goal.pose.orientation.w = 1

    ang_goal_pub.publish(goal)

    pose_index = (current_index + vel_lookahead_dist) % plan_size


    goal                    = PoseStamped()
    goal.header.seq         = seq
    goal.header.stamp       = rospy.Time.now()
    goal.header.frame_id    = frame_id
    goal.pose.position.x    = plan[pose_index][1]
    goal.pose.position.y    = plan[pose_index][2]
    goal.pose.orientation.z = 0
    goal.pose.orientation.w = 1

    seq = seq + 1

    vel_goal_pub.publish(goal)




     

if __name__ == '__main__':
    try:
        rospy.init_node('target_manager', anonymous = True)
        if not plan:
            rospy.loginfo('obtaining trajectory')
            construct_path()
        #rospy.Subscriber('/{}/purepursuit_control/latched_index'.format(car_name),Int64,index_callback)
        rospy.Subscriber('/gazebo/model_states', ModelStates, odom_callback)
	    #print "node running test"
        rospy.spin()
    except rospy.ROSInterruptException:
        pass