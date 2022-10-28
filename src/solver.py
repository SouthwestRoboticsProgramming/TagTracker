# Solves for robot position based on results of found tags
# from main import logger
# TODO: Make logging work
import numpy as np

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
			# logger.error('No tags defined! Quitting')
			raise Exception('No tags defined in environment JSON')
		self.tags_dict = {}
		for tag in environment_dict['tags']:
			self.tags_dict[tag['id']] = tag

		self.tag_family = environment_dict['tag_family']

		if self.tag_family != "36h11":
			'''logger.warning('Are you sure that you want to look for, tags in the \
				 family {}. FRC uses 36h11'.format(self.tag_family))
			'''
	def solve(self, detection_poses):
		# if not detection_poses:
		#     return

		# Master list of estimated poses to be combined
		estimated_poses_list = []

		test_matrices = []

		# Apply camera and tag pose to estimated pose
		for pose_dict in detection_poses:
			estimated_pose = pose_dict['pose']
			camera_pose = pose_dict['camera'].robot_position
			tag_id = pose_dict['tag_id']
			tag_family = pose_dict['tag_family']

			# Find the tag info that matches that tag
			if not (self.tag_family in str(tag_family)):
				# TODO: Log warning
				break

			# Get the info for the tag
			tag_dict = self.tags_dict[tag_id]

			if not tag_dict:
				# TODO: Log warning
				break

			tag_pose = tag_dict['transform']

			# Convert to numpy arrarys for math
			estimated_pose = np.array(estimated_pose)
			camera_pose = np.array(camera_pose)
			tag_pose = np.array(tag_pose)

			size = tag_dict['size']
			estimated_pose[0][3] *= size
			estimated_pose[1][3] *= -size # TODO: Should this be negative?
			estimated_pose[2][3] *= size
			test_matrices.append(estimated_pose)

			# Take into account pose of the camera and tag
			apply_camera = invert(tag_pose)
			apply_tag = invert(camera_pose)

			with_camera = np.matmul(estimated_pose, apply_camera)
			with_tag = np.matmul(with_camera, apply_tag)
			# TODO: Test with rotation

			# test_matrices.append(with_tag)

			# Split into x, y, z
			final_pose = np.array([-with_tag[0][3], # X has to be inverted
									with_tag[1][3],
									with_tag[2][3]])

			estimated_poses_list.append(final_pose)


		# Combine poses with average (just for position, not rotation)
		
		return ((0, 0, 0), test_matrices)

		# total = sum(estimated_poses_list)
		# average = total / len(estimated_poses_list)

		# return average
	