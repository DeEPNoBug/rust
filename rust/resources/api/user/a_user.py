#coding: utf8

from rust.core.business import ParamObject
from rust.core.api import ApiResource
from rust.core.decorator import param_required
from rust.core.exceptions import BusinessError
from rust.resources.business.user.encode_service import EncodeService
from rust.resources.business.user.fill_service import FillService

from rust.resources.business.user.user_factory import UserFactory
from rust.resources.business.permission.permission_group_repository import PermissionGroupRepository

import settings

from rust.resources.business.user.user_repository import UserRepository


class AUser(ApiResource):
	"""
	用户
	"""
	app = 'rust.user'
	resource = 'user'

	@param_required(['user', 'user_id:int', '?with_options:json'])
	def get(params):
		target_user = UserRepository().get_by_id(params['user_id'])
		with_options = params.get('with_options')
		if with_options:
			FillService().fill([target_user], with_options)
		return EncodeService().encode(target_user, with_options)

	@param_required(['user', 'username', '?group_id:int'])
	def put(params):
		"""
		创建用户只能由管理员操作，且只能初始化登录名和分组(角色)
		"""
		if not params['user'].is_manager:
			raise BusinessError(u'操作无权限')
		param_object = ParamObject({
			'username': params['username'],
			'password': settings.DEFAULT_PASSWORD if hasattr(settings, 'DEFAULT_PASSWORD') else '123456'
		})
		user = UserFactory().create(param_object)
		if params.get('group_id'):
			group = PermissionGroupRepository().get_by_id(params['group_id'])
			if group:
				group.add_user(user)
		return {
			'id': user.id
		}

	@param_required(['user', '?nickname', '?avatar', '?group_id:int'])
	def post(params):
		param_object = ParamObject({
			'nickname': params.get('nickname'),
			'password': params.get('password'),
			'avatar': params.get('avatar')
		})
		UserFactory(params['user']).update(param_object)
		if params.get('group_id'):
			group = PermissionGroupRepository().get_by_id(params['group_id'])
			if group:
				group.add_user(params['user'])
		return {}