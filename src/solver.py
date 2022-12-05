# Solves for robot position based on results of found tags
import numpy as np
from main import logger

# TODO-Ryan: Finish/Fix

# Manual implementation of matrix inversion because np.linalg.inv is slow
def invert(m):
	m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33 = np.ravel(m)
	a2323 = m22 * m33 - m23 * m32
	a1323 = m21 * m33 - m23 * m31
	a1223 = m21 * m32 - m22 * m31
	a0323 = m20 * m33 - m23 * m30
	a0223 = m20 * m32 - m22 * m30
	a0123 = m20 * m31 - m21 * m30
	a2313 = m12 * m33 - m13 * m32
	a1313 = m11 * m33 - m13 * m31
	a1213 = m11 * m32 - m12 * m31
	a2312 = m12 * m23 - m13 * m22
	a1312 = m11 * m23 - m13 * m21
	a1212 = m11 * m22 - m12 * m21
	a0313 = m10 * m33 - m13 * m30
	a0213 = m10 * m32 - m12 * m30
	a0312 = m10 * m23 - m13 * m20
	a0212 = m10 * m22 - m12 * m20
	a0113 = m10 * m31 - m11 * m30
	a0112 = m10 * m21 - m11 * m20

	det = m00 * (m11 * a2323 - m12 * a1323 + m13 * a1223) \
		- m01 * (m10 * a2323 - m12 * a0323 + m13 * a0223) \
		+ m02 * (m10 * a1323 - m11 * a0323 + m13 * a0123) \
		- m03 * (m10 * a1223 - m11 * a0223 + m12 * a0123)
	det = 1 / det

	return np.array([ \
		det *  (m11 * a2323 - m12 * a1323 + m13 * a1223), \
		det * -(m01 * a2323 - m02 * a1323 + m03 * a1223), \
		det *  (m01 * a2313 - m02 * a1313 + m03 * a1213), \
		det * -(m01 * a2312 - m02 * a1312 + m03 * a1212), \
		det * -(m10 * a2323 - m12 * a0323 + m13 * a0223), \
		det *  (m00 * a2323 - m02 * a0323 + m03 * a0223), \
		det * -(m00 * a2313 - m02 * a0313 + m03 * a0213), \
		det *  (m00 * a2312 - m02 * a0312 + m03 * a0212), \
		det *  (m10 * a1323 - m11 * a0323 + m13 * a0123), \
		det * -(m00 * a1323 - m01 * a0323 + m03 * a0123), \
		det *  (m00 * a1313 - m01 * a0313 + m03 * a0113), \
		det * -(m00 * a1312 - m01 * a0312 + m03 * a0112), \
		det * -(m10 * a1223 - m11 * a0223 + m12 * a0123), \
		det *  (m00 * a1223 - m01 * a0223 + m02 * a0123), \
		det * -(m00 * a1213 - m01 * a0213 + m02 * a0113), \
		det *  (m00 * a1212 - m01 * a0212 + m02 * a0112)  \
	]).reshape(4, 4)

class RobotPoseSolver:
	def __init__(self, environment_dict):
		# Unpack tag positions into lookup dictionary
		if not environment_dict['tags']:
			logger.error('No tags defined! Quitting')
			raise AssertionError('No tags defined in environment JSON')
		self.tags_dict = {tag['id']: tag for tag in environment_dict['tags']}
		self.tag_family = environment_dict['tag_family']

		if self.tag_family != "tag16h5":
			'''logger.warning('Are you sure that you want to look for, tags in the \
				family {}. FRC uses 16h5'.format(self.tag_family))
			'''
	def solve(self, detection_poses):
		# Master list of estimated poses to be combined
		estimated_poses_list = []

		# Apply camera and tag pose to estimated pose
		for pose_dict in detection_poses:
			estimated_pose = pose_dict['pose']
			camera_pose = pose_dict['camera'].robot_position
			tag_id = pose_dict['tag_id']
			tag_family = pose_dict['tag_family']

			# Find the tag info that matches that tag
			if self.tag_family not in str(tag_family):
				logger.warning(f"Found a tag that doesn't belong to {self.tag_family}")
				continue

			# Get the info for the tag
			tag_dict = self.tags_dict.get(tag_id)

			if not tag_dict:
				logger.warning(f"Found a tag that isn't defined in environment. ID: {tag_id}")
				continue

			tag_pose = tag_dict['transform']

			# Convert to numpy arrarys for math
			estimated_pose = np.array(estimated_pose)
			camera_pose = np.array(camera_pose)
			tag_pose = np.array(tag_pose)

			# Scale estimated position by tag size
			size = tag_dict['size']
			estimated_pose[0][3] *= size
			estimated_pose[1][3] *= size
			estimated_pose[2][3] *= size

			# Find where the camera is if the tag is at the origin
			tag_relative_camera_pose = invert(estimated_pose)

			# Find the camera position relative to the tag position
			world_camera_pose = np.matmul(tag_pose, tag_relative_camera_pose)

			# Find the position of the robot from the camera position
			inv_rel_camera_pose = invert(camera_pose)
			robot_pose = np.matmul(world_camera_pose, inv_rel_camera_pose)

			estimated_poses_list.append(robot_pose)

		# Combine poses with average (just for position, not rotation)

		if not estimated_poses_list:
			# If we have no samples, report none
			return (None, estimated_poses_list)
			
		# TODO: Figure out rotation
		total = np.array([0.0, 0.0, 0.0])
		for pose in estimated_poses_list:
			total += np.array([pose[0][3], pose[1][3], pose[2][3]])
		average = total / len(estimated_poses_list)
		return (average, estimated_poses_list)
